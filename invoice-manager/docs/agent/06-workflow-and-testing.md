# Workflow And Testing

## Development Workflow
1. Start backend and verify `/health`.
2. Implement feature in smallest responsible module.
3. Add/update tests for behavior changes.
4. Run local checks before commit.

## Testing Focus
- API route behavior and validation
- recurring generation logic
- payment state transitions
- integration failures (external API timeout/errors)

## Commit Guidance
- Keep commits small and focused.
- Use imperative subject lines.
- Document schema or API contract changes clearly.

## Change Checklist
- Does the change preserve API response shape?
- Are error states handled and surfaced?
- Is new code split into maintainable files?
- Are file size limits respected?

