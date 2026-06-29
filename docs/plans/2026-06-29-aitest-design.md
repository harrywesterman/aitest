# aitest — AI Android Test Framework

## Overzicht

Open-source Python CLI tool die Android telefoons + voorgeïnstalleerde apps autonoom verkent via Appium en AI (lokale LLM), daar pytest testscripts van genereert, en deze parallel op 8+ USB-devices draait.

## Doel

- Vaste test suite voor Android OS (`tests/android/`) — handgemaakt, eenmalig
- AI-gegeneerde tests per voorgeïnstalleerde app (`tests/apps/`)
- Triggers: Android update, app update, nieuw telefoontype
- Self-healing: bij falende tests zoekt AI nieuwe selectoren
- Notificatie: CLI exit code + webhook als een test faalt

## Architectuur

```
CLI (typer)
  ├── LLM Client (OpenAI-compatibel: url + api_key + model)
  ├── Device Manager (ADB, Appium parallel op unieke poorten)
  ├── Explorer Agent (AI verkent phone/app, genereert testplan)
  ├── Test Runner (pytest parallel, JUnit XML output)
  ├── Healer (AI herstelt gebroken tests bij UI wijzigingen)
  └── Notifier (webhook / logging)
```

## Config (aitest.yaml)

```yaml
llm:
  url: "https://ollama.lan/v1"
  key: ""
  model: "qwen2.5:7b"

devices:
  - serial: "R58N910xxx1"
    model: "Samsung Galaxy S24"
    port: 4723

notify:
  webhook: ""
```

## Projectstructuur

```
aitest/
├── aitest/                  # Python package
│   ├── cli.py              # typer CLI
│   ├── config.py           # config laden
│   ├── llm_client.py       # OpenAI-compat API
│   ├── device.py           # ADB + Appium manager
│   ├── explorer.py         # AI verkent phone/app
│   ├── generator.py        # testplan → pytest code
│   ├── runner.py           # parallelle executor
│   ├── healer.py           # self-healing
│   └── notifier.py         # webhook / logging
├── tests/
│   ├── android/            # vaste Android OS tests
│   │   ├── test_settings.py
│   │   ├── test_notifications.py
│   │   ├── test_navigation.py
│   │   ├── test_permissions.py
│   │   ├── test_accounts.py
│   │   ├── test_hardware.py
│   │   ├── test_connectivity.py
│   │   └── conftest.py
│   └── apps/               # AI-gegeneerd per app
│       └── ...
├── pyproject.toml
├── aitest.yaml.example
└── README.md
```

## CLI Commands

```
aitest explore --app com.example.app     # AI verkent 1 app
aitest explore --all                     # AI verkent alle apps
aitest run                               # draait complete suite
aitest run --device <serial>             # op 1 device
aitest heal --test tests/apps/app.py     # AI herstelt test
aitest devices list                      # toont devices
```

## AI Exploratie Flow

1. App openen → page source (XML) + screenshot ophalen
2. LLM analyseert: elementen herkennen, asserts genereren
3. LLM beslist welke actie logisch is (klik, type, swipe)
4. Actie uitvoeren → nieuw scherm → herhaal
5. Volledige app doorlopen → pytest .py genereren

## Self-Healing Flow

1. Test faalt (bv. resource-id gewijzigd)
2. AI krijgt screenshot + oude test code
3. AI vindt nieuwe selector op basis van screenshot
4. Test wordt geüpdatet

## Beslissingen

- **Test runner:** pytest
- **Notificatie:** CLI (fase 1), webhook (fase 2)
- **LLM:** OpenAI-compatibel (Ollama, vLLM, LM Studio, OpenAI)
- **Test output:** stand-alone pytest + Appium scripts
