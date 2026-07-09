## Why

The ScholarshipFinder project has a README describing its purpose and suggested structure, but no actual code, configuration, or module skeleton exists yet. This change establishes the foundational project scaffold so development can begin.

## What Changes

- Create `pyproject.toml` with project metadata and tool config (black, ruff, pytest)
- Create `.gitignore` for Python/uv/editor artifacts
- Create `src/scholarship_finder/` package with stub modules for core entities
- Create `tests/` directory with test scaffolding
- Establish the importable package structure matching the README's suggested layout

## Capabilities

### New Capabilities
- `project-scaffold`: Initial Python project configuration, package skeleton, and test scaffolding

### Modified Capabilities

None — this is the initial setup.

## Impact

- New files: `pyproject.toml`, `.gitignore`, package source files, test files
- No existing code is affected
- Dependencies: `uv` for environment management, `black`/`ruff`/`pytest` for tooling
