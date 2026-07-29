# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

## Quality checks

```bash
ruff check .
pytest
python -m compileall -q app ui scripts run_project.py
```

## Pull requests

- Keep changes focused.
- Add or update tests for deterministic logic.
- Do not commit API keys, uploaded documents, vector stores, or model caches.
- Document user-visible behavior changes.
- Include screenshots for UI changes.
