# Contributing

## Commit discipline

Keep commits atomic and use descriptive Conventional Commit messages:

- `feat(scope): ...` for behaviour
- `fix(scope): ...` for corrections
- `test(scope): ...` for test-only changes
- `docs(scope): ...` for documentation
- `chore(scope): ...` for maintenance

Avoid messages such as `updates`, `changes`, or `fix stuff`.

## Required checks

Run before every pull request:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Do not commit live operational data. Use synthetic fixtures and placeholders.

