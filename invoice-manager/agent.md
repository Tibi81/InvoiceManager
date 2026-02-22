# Invoice Manager - Agent Rules

This file is the compact entrypoint for AI collaboration in this repository.
Detailed guidance is split into `docs/agent/*.md`.

## Mandatory File Size Policy

From now on, new and modified files must follow:
- Target: `50-150` lines per file.
- Acceptable upper bound: `200` lines.
- `200-300` lines only if strictly necessary.
- Over `300` lines is not acceptable for normal development.

If a file grows too large:
- split by responsibility (API route/service/formatter/view/dialog/state)
- move helper logic to dedicated modules
- keep entrypoint files thin

## Documentation Map

- `docs/agent/01-overview.md`
- `docs/agent/02-architecture.md`
- `docs/agent/03-models-and-api.md`
- `docs/agent/04-coding-guidelines.md`
- `docs/agent/05-integrations.md`
- `docs/agent/06-workflow-and-testing.md`
- `docs/agent/07-debugging-and-resources.md`

## Working Agreement

- Prefer small, focused edits.
- Preserve existing behavior unless change is requested.
- Validate critical flows after refactor.
- Keep API contracts consistent across backend, web, and desktop.

