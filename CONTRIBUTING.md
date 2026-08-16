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
python3 tools/project_instructions.py check
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

After any lasting policy-source change, review `project/INSTRUCTIONS.md.tmpl` and update `project/POLICY_SOURCE.sha256` with the value printed by `python3 tools/project_instructions.py fingerprint`. A fingerprint refresh attests that the complete project-instructions contract was reviewed; it is not a substitute for changing the text when the bootstrap contract changed.

Do not commit live operational data. Use synthetic fixtures and placeholders.
