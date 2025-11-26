# Contributing

Thank you for your interest in improving the Confidential Computing Lab! Contributions are welcome for features, documentation, examples, and tests.

## Development Workflow
1. Fork the repository and create a feature branch.
2. Install dependencies with `pip install -e .[dev]`.
3. Format and lint code with `ruff` and `black` (`ruff check .` and `black .`).
4. Add or update tests under `tests/` and run `pytest`.
5. Submit a pull request describing the change, motivation, and testing performed.

## Coding Standards
- Prefer typed functions, clear names, and docstrings for every public function or class.
- Handle errors explicitly; never ignore exceptions.
- Avoid hard-coded secrets or environment-dependent logic.
- Keep documentation up to date alongside code changes.

## Reporting Security Issues
Please follow the process outlined in [SECURITY.md](SECURITY.md). Do not open public issues for suspected vulnerabilities.

## Community Expectations
All contributors and maintainers must adhere to the [Code of Conduct](CODE_OF_CONDUCT.md).
