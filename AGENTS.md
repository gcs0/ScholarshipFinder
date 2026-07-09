## /lint

Run the linter:

```
ruff check .
```

## /format

Format code with Black:

```
black .
```

## /test

Run tests with pytest:

```
pytest
```

## /check

Run all linting, formatting check, and tests:

```
ruff check . && black --check . && pytest
```
