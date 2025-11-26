# Confidential Computing Lab

A fully local, educational lab that simulates Intel SGX-style enclaves and AMD SEV-style encrypted VMs. The project exposes a validated FastAPI service, mock KMS/HSM, demo workloads, dashboard assets, Rust enclave stubs, and comprehensive documentation for teaching confidential computing concepts safely.

## Features
- **Enclave Simulation (SGX-inspired)**: loading, measurement (mock MRENCLAVE), ECALL/OCALL flow, sealed storage, and simulated attestation.
- **SEV VM Model**: encrypted memory pages, vCPU launch, VM measurement, and attestation flows.
- **Confidential Computing API**: REST endpoints for compute, sealing, attestation, VM launch, page encryption, and health checks.
- **Demo Workloads**: encrypted keyword search, sealed secret manager, privacy-preserving inference placeholder, and integrity-protected counter.
- **Security Hygiene**: strict input validation, structured logging, deterministic key derivation, and explicit educational disclaimers.
- **Documentation & Dashboard**: architecture diagrams, API reference, and static dashboard for visual exploration.

## Repository Layout
```
.
├── dashboard/                 # Static HTML/JS/CSS assets for the lab dashboard
├── docs/                      # Architecture and API reference
├── enclave/                   # Rust enclave stubs (no SGX hardware required)
├── server/                    # FastAPI app, routes, simulations, security helpers, workloads
├── sev/                       # SEV VM simulation modules
├── tests/                     # Pytest suite exercising API and validations
├── pyproject.toml             # Project configuration and optional dev tooling
└── requirements.txt           # Runtime dependencies (duplicated for convenience)
```

## Architecture
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for diagrams, lifecycle descriptions, and security posture.

## Getting Started
1. **Install dependencies** (Python 3.10+)
   ```bash
   pip install -e .[dev]
   ```
   Or use the convenience targets:
   ```bash
   make install      # install runtime + dev dependencies
   make check        # black --check, ruff check, pytest
   ```
2. **Run the API**
   ```bash
   uvicorn server.api:app --reload
   ```
3. **Exercise the endpoints**
   - Use the interactive docs at `http://localhost:8000/docs`
   - Refer to [docs/API.md](docs/API.md) for payload examples
4. **Run tests**
   ```bash
   pytest
   ```
5. **Launch the dashboard** (optional)
   ```bash
   python -m http.server 8001
   # then open http://localhost:8001/dashboard/index.html
   ```

### Development Environment
- **Dev Container**: `.devcontainer/devcontainer.json` provisions a VS Code Remote container with Python 3.11 and auto-installs dev dependencies. Open the repo in VS Code and reopen in container to get a consistent toolchain (ruff, black, pytest).
- **Make targets**: `make lint`, `make format`, `make test`, and `make serve` streamline common workflows.

## Demo Workloads
- **keyword_search**: Counts keyword occurrences across provided documents.
- **sealed_secret**: Seals a secret to an identity, immediately unseals to demonstrate retrieval.
- **inference**: Computes an L2 norm and commitment hash over a numeric vector.
- **counter**: Increments a counter with a simple integrity MAC.

## Security Notes
- All cryptography is **educational** and uses standard library primitives for transparency.
- Keys are derived deterministically from identity + context via the mock KMS; do **not** use for production secrets.
- Attestation, isolation, and measurements are simulations and provide no hardware-backed guarantees.
- Input validation and logging are in place to keep the lab safe and auditable.

## Development Guidelines
- Use `ruff` and `black` (configured in `pyproject.toml`) for linting and formatting.
- Prefer typed functions and docstrings; follow the patterns in existing modules.
- Add tests for new behaviours under `tests/`.
- Continuous Integration runs ruff, black, and pytest on pushes and pull requests via `.github/workflows/ci.yml`.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow guidance and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community expectations. Security issues should follow [SECURITY.md](SECURITY.md).

## License
Licensed under the [MIT License](LICENSE).
