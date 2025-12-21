# Submit Changes

Create a feature branch, commit changes, push to remote, and open a pull request.

## Instructions

1. Determine the engineer's initials:
   - Run `git config user.name` to get the full name
   - Extract initials from the name (e.g., "Phil Long" → "pl")
   - Convert to lowercase for consistency
2. Analyze the current work and changes made in this session
3. Generate a descriptive feature name in kebab-case based on the changes
4. Create a new branch with format: `<initials>/<feature-description-in-kebab-case>`
   - Example: `pl/add-user-authentication`
   - Example: `jd/fix-payment-validation`
   - Example: `sk/refactor-api-client`
5. Stage all relevant changes using `git add`
6. Create a commit with a clear, descriptive message following the repo's commit style
7. If the commit fails due to pre-commit hooks:
   - Check if hooks auto-formatted files (e.g., ruff, prettier)
   - If so, stage the reformatted files: `git add -u`
   - Retry the same commit command (commit never happened, so just try again)
8. Push the branch to origin with: `git push -u origin <branch-name>`
9. Create a pull request using `gh pr create` with:
   - A clear, descriptive title
   - A detailed description including:
     - Summary of changes (2-3 bullet points)
     - Test plan (how to verify the changes)
     - Any relevant context or notes
10. Display the PR URL for review

## Notes

- Branch naming: Always use `<initials>/` prefix followed by kebab-case description
- Initials should be lowercase (e.g., "pl" not "PL")
- Commit messages: Use imperative mood (e.g., "add feature" not "added feature")
- PR description: Be thorough but concise - focus on the "why" and "what"
- The PR will automatically include Claude Code attribution footer
- Base branch is `main` (check git status to confirm)
- Don't commit lockfiles, env files, or generated artifacts
- Run `make check-all` before submitting if changes are significant
