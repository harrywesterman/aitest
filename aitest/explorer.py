import json
import logging
import re
import time
from .llm_client import LLMClient

logger = logging.getLogger(__name__)

EXPLORER_SYSTEM_PROMPT = """You are an Android test engineer exploring an app. You are given the XML page source.

Return ONLY valid JSON (no markdown, no code fences):
{
  "description": "what this screen does",
  "elements": [
    {
      "selector_type": "id | xpath | text | description | accessibility_id",
      "selector_value": "the selector value",
      "assertion": "Appium assertion code using AppiumBy"
    }
  ],
  "action": {
    "type": "tap | type | back | terminate",
    "selector_type": "id | xpath | text",
    "selector_value": "element to interact with",
    "value": "text to type if type action"
  },
  "is_end_state": false
}

Guidelines:
- Write assertions for STABLE UI elements only (labels, buttons, tabs, menu items)
- IGNORE dynamic values like: times (e.g. 05:10, 22:00:19), dates, counters
- Use "id" (resource-id) for selector_type when available in XML
- Use "text" for matching by visible text (e.g. the text attribute)
- Use "description" or "accessibility_id" for content-desc / accessibility labels when available
- Use "xpath" for selector_type for complex matches
- Prefer AppiumBy.ACCESSIBILITY_ID for content-desc elements, and AppiumBy.ANDROID_UIAUTOMATOR with UiSelector().text(...) for visible labels
- Your action MUST explore the app: tap tabs, tap buttons, tap menu items
- NEVER use "back" or "terminate" when tabs or buttons are visible
- Explore at least 3-4 different screens before terminating
- DO NOT test for text that looks like a time (HH:MM or HH:MM:SS) or dates
- For assertions, prefer content-desc / accessibility labels for clickable controls, and visible text for static labels when that is the stable identifier"""


class ExplorerAgent:
    def __init__(self, llm_url: str, llm_key: str = "", model: str = "qwen2.5:7b"):
        self.llm_client = LLMClient(url=llm_url, key=llm_key, model=model)
        self.max_screens = 10
        self._poll_interval = 0.5

    def explore_app(self, driver, app_package: str) -> list[dict]:
        screens = []
        seen = set()

        self._wait_for_screen(driver)

        for step in range(self.max_screens):
            self._wait_for_screen(driver)
            page_source = driver.page_source
            compressed = self._compress_xml(page_source)

            h = hash(compressed)
            if h in seen:
                break
            seen.add(h)

            analysis = self.analyze_screen(page_source, app_package, compressed)
            analysis["step"] = step
            screens.append(analysis)

            if analysis.get("is_end_state"):
                break

            if not self._do_action(driver, analysis):
                break

        return screens

    @staticmethod
    def _compress_xml(page_source: str) -> str:
        attrs_keep = {"resource-id", "text", "content-desc", "clickable", "checkable", "scrollable", "class"}
        lines = page_source.split("\n")
        out = []
        for line in lines:
            if all(f"{a}=\"" not in line for a in attrs_keep):
                continue
            pairs = re.findall(r'([-\w.]+)=["\']([^"\']*)["\']', line)
            tag = re.match(r'\s*<([^>\s]+)', line)
            if not tag:
                continue
            cls_name = tag.group(1).split(".")[-1]
            kept = [f"<{cls_name}"]
            seen_flags = set()
            for k, v in pairs:
                if k not in attrs_keep or not v:
                    continue
                if k == "class":
                    kept.append(f"class={v.split('.')[-1]}")
                elif k == "content-desc" and v:
                    kept.append(f"desc=\"{v}\"")
                elif k == "resource-id" and v:
                    kept.append(f"id=\"{v}\"")
                elif k == "text" and v:
                    kept.append(f"text=\"{v}\"")
                elif k in ("clickable", "checkable", "scrollable") and v == "true" and k not in seen_flags:
                    kept.append(k)
                    seen_flags.add(k)
            kept.append(">")
            out.append(" ".join(kept))
        return "\n".join(out[:80])

    @staticmethod
    def _strip_markdown(text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3].strip()
        if text.startswith("json"):
            text = text[4:].strip()
        return text

    def analyze_screen(self, page_source: str, app_package: str = "", compressed: str = "") -> dict:
        if not compressed:
            compressed = self._compress_xml(page_source)
        messages = [
            {"role": "system", "content": EXPLORER_SYSTEM_PROMPT},
            {"role": "user", "content": f"App package: {app_package}\n\nPage source:\n{compressed}"},
        ]
        try:
            text = self.llm_client.chat(messages, temperature=0.1)
            text = self._strip_markdown(text)
            parsed = json.loads(text)
            return parsed
        except json.JSONDecodeError:
            logger.warning("LLM returned invalid JSON, navigating back")
            return {
                "description": "screen",
                "elements": [],
                "action": {"type": "back"},
                "is_end_state": False,
            }
        except Exception as e:
            logger.error("LLM call failed: %s", e)
            return {
                "description": "screen",
                "elements": [],
                "action": {"type": "back"},
                "is_end_state": True,
            }

    def _do_action(self, driver, analysis: dict) -> bool:
        from appium.webdriver.common.appiumby import AppiumBy

        action = analysis.get("action", {})
        t = action.get("type", "back")

        if t == "terminate":
            return False
        if t == "back":
            driver.back()
            return True

        sel_type = action.get("selector_type", "xpath")
        sel_val = action.get("selector_value", "")

        if not sel_val:
            driver.back()
            return True

        by_map = {
            "id": AppiumBy.ID,
            "xpath": AppiumBy.XPATH,
            "text": AppiumBy.XPATH,
            "description": AppiumBy.ACCESSIBILITY_ID,
            "content-desc": AppiumBy.ACCESSIBILITY_ID,
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
            "uiautomator": AppiumBy.ANDROID_UIAUTOMATOR,
        }
        by = by_map.get(sel_type, AppiumBy.XPATH)
        if sel_type == "text":
            sel_val = f"//*[@text='{sel_val}']"

        try:
            if t == "type":
                el = driver.find_element(by, sel_val)
                el.clear()
                el.send_keys(action.get("value", ""))
            else:
                el = driver.find_element(by, sel_val)
                el.click()
            time.sleep(self._poll_interval)
            return True
        except Exception:
            driver.back()
            return True

    @staticmethod
    def _wait_for_screen(driver, timeout: int = 10) -> None:
        start = time.time()
        while time.time() - start < timeout:
            try:
                src = driver.page_source
                if src and len(src) > 100:
                    return
            except Exception:
                pass
            time.sleep(0.3)
