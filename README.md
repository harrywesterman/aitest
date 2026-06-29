# aitest

AI-powered Android Appium test generator. Run fully locally with your own LLM.

## Quick start

```bash
pip install aitest

# Configure
cp aitest.yaml.example aitest.yaml
# Edit aitest.yaml with your LLM URL and devices

# Explore an app
aitest explore --app com.example.app

# Run all tests on all devices
aitest run

# Fix a failing test
aitest heal tests/apps/test_app.py
```
