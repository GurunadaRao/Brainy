# Contributing to Brainy 1.0

Thank you for your interest in contributing to Brainy! We welcome contributions to our ingestion pipelines, GraphRAG algorithms, and frontend interfaces.

## Rules of Engagement
1. **Prioritize Code Quality**: All code changes must align with instructions listed in [INSTRUCTIONS.md](file:///.ai/instructions/INSTRUCTIONS.md).
2. **Write Tests**: Pull requests without matching unit or integration tests will not be reviewed.
3. **Keep PRs Scope-Focused**: Avoid large, sprawling pull requests. Keep commits atomic.

## How to Submit a Pull Request
1. Fork the repository and create your feature branch: `git checkout -b feature/my-new-feature`.
2. Ensure your changes pass lints and formatting checks:
   ```bash
   black --check src/ tests/
   flake8 src/ tests/
   mypy src/
   ```
3. Run the pytest suite to verify logic correctness:
   ```bash
   pytest tests/
   ```
4. Commit your changes following Semantic Commit Messages (e.g., `feat(ingest): add audio downloader`).
5. Open a Pull Request referencing the issue number.

## Commit Message Conventions
We follow conventional commits style:
- `feat`: A new user-facing feature.
- `fix`: A bug fix.
- `docs`: Documentation-only changes.
- `style`: Changes that do not affect the meaning of the code (formatting, white-space, etc).
- `refactor`: A code change that neither fixes a bug nor adds a feature.
- `test`: Adding missing tests or correcting existing tests.
- `chore`: Internal repository maintenance tasks.
