## 1. Project Configuration

- [x] 1.1 Create `pyproject.toml` with project metadata (name, version, description, requires-python)
- [x] 1.2 Add `[tool.black]` section to pyproject.toml
- [x] 1.3 Add `[tool.ruff]` section to pyproject.toml
- [x] 1.4 Add `[tool.pytest.ini_options]` section to pyproject.toml
- [x] 1.5 Add `[dependency-groups]` for dev dependencies (black, ruff, pytest)
- [x] 1.6 Create `.gitignore` with entries for `.venv/`, `__pycache__/`, `*.pyc`, and editor artifacts

## 2. Package Skeleton

- [x] 2.1 Create `src/scholarship_finder/` package directory with `__init__.py`
- [x] 2.2 Create `src/scholarship_finder/user.py` stub module
- [x] 2.3 Create `src/scholarship_finder/scholarship.py` stub module
- [x] 2.4 Create `src/scholarship_finder/scholarship_request.py` stub module

## 3. Test Scaffolding

- [x] 3.1 Create `tests/` directory with `__init__.py`
- [x] 3.2 Create placeholder test file (e.g., `tests/test_placeholder.py`)

## 4. Verify Tooling

- [ ] 4.1 Run `ruff check .` and confirm it exits with code 0
- [ ] 4.2 Run `black --check .` and confirm it exits with code 0
- [ ] 4.3 Run `pytest --collect-only` and confirm tests are discovered
