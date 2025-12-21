# Pre-Release Checks

Run all pre-release checks (backend lint, frontend lint, frontend build) and iteratively fix any issues found.

## Instructions

1. Run `make check-all` to execute all pre-release checks
2. If any check fails:
   - Analyze the error messages carefully
   - Fix the issues in the relevant files
   - Re-run `make check-all` to verify the fixes
   - Repeat until all checks pass
3. Continue this process until all three checks pass:
   - Backend linting (ruff check + ruff format)
   - Frontend linting (ESLint)
   - Frontend production build
4. Report a summary of what was fixed

## Notes

- For backend linting errors, focus on the ruff error messages
- For frontend linting errors, focus on ESLint warnings/errors
- For frontend build errors, look for TypeScript type errors or React issues
- Make sure to read the full error output before attempting fixes
- If ruff format makes changes, those are auto-fixes and you should verify they were applied correctly
