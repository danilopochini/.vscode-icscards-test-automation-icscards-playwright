# ICS Cards Playwright tests

Python + pytest + Playwright, using the Page Object pattern, against https://www.icscards.nl.

## Setup
```powershell
cd icscards-tests
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

## Run
```powershell
pytest                          # all tests, headless, full speed; report.html opens at the end
pytest -m smoke                 # smoke only
pytest --headed --slowmo 500    # visible browser with 500 ms slow-motion
pytest --no-open-report         # don't open the report (e.g. on CI)
pytest --browser firefox --browser webkit
pytest --base-url https://www.icscards.nl
```
Every run writes an HTML report to `report.html` and opens it in your default browser.
Failures keep a screenshot and trace in `test-results/` (`playwright show-trace <trace.zip>`).

## Layout
- `pages/` page objects (`BasePage`, `HomePage`)
- `tests/` test modules
- `conftest.py` fixtures (nl-NL locale, `home` fixture)
