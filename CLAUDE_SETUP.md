# Claude Code Setup Guide for New Engineers

Welcome to the Arive team! This guide will help you set up Claude Code with all the custom skills, MCP servers, and automation that will supercharge your development workflow.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Claude Code Installation](#claude-code-installation)
3. [Project-Specific Setup](#project-specific-setup)
4. [Available Custom Skills](#available-custom-skills)
5. [MCP Servers](#mcp-servers)
6. [Automation Hooks](#automation-hooks)
7. [Daily Workflow Examples](#daily-workflow-examples)
8. [Tips for "Vibe Coding"](#tips-for-vibe-coding)

---

## Prerequisites

Before setting up Claude Code, ensure you have:

- [ ] macOS, Linux, or Windows with WSL2
- [ ] Git installed and configured
- [ ] Node.js 18+ and pnpm installed
- [ ] Python 3.13+ and uv installed
- [ ] Docker Desktop installed and running
- [ ] Access to this GitHub repository
- [ ] PostgreSQL client tools (optional, for database access)

## Claude Code Installation

### 1. Install Claude Code CLI

```bash
# Install Claude Code
curl -fsSL https://cli.claude.ai/install.sh | sh

# Verify installation
claude --version
```

### 2. Authenticate

```bash
# Log in to Claude
claude auth login
```

Follow the browser prompts to authenticate with your Anthropic account.

### 3. Set Up Global Configuration

Create your personal settings file:

```bash
mkdir -p ~/.claude
```

**Optional**: Configure personal preferences in `~/.claude/settings.json`:

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "alwaysThinkingEnabled": false
}
```

---

## Project-Specific Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd arive
```

### 2. Environment Variables for MCP Servers

The project uses MCP servers that require environment variables. Set these up:

**For GitHub MCP** (optional but recommended):
```bash
# Create a GitHub personal access token at:
# https://github.com/settings/tokens/new
# Required scopes: repo, read:org

export GITHUB_TOKEN="your_github_token_here"

# Add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export GITHUB_TOKEN="your_github_token_here"' >> ~/.zshrc
```

**For Database MCP** (uses local development database by default):
```bash
# Default connection (no setup needed):
# postgresql://postgres:postgres@localhost:5432/arive_dev

# Optional: Override with custom connection string
export DATABASE_URL="postgresql://user:pass@host:port/database"
```

### 3. Install Project Dependencies

```bash
# Install all dependencies (frontend + backend)
make install

# Start development database
make db-start

# Apply database migrations
make db-upgrade
```

### 4. Verify Claude Code Setup

The project includes:
- ✅ `.claude/skills/` - Custom workflow skills
- ✅ `.claude/settings.json` - Project-specific automation and permissions
- ✅ `.mcp.json` - MCP server configurations
- ✅ `CLAUDE.md` - Codebase instructions

Start Claude Code in the project directory:

```bash
claude code
```

You should see a message indicating the project configuration loaded successfully.

---

## Available Custom Skills

Claude Code will automatically use these skills when relevant. You can also invoke them directly:

### `/db-workflow`
**When it activates**: Modifying database models, creating migrations, or managing Alembic

**What it does**:
- Guides through complete database migration workflow
- Ensures migrations are reviewed before applying
- Prevents accidental data loss
- Runs tests after migrations

**Example use**: "I need to add a new field to the User model"

---

### `/test-workflow`
**When it activates**: Writing tests, fixing test failures, or validating code changes

**What it does**:
- Runs backend tests with pytest
- Runs frontend tests (if applicable)
- Performs type checking (basedpyright for backend, TypeScript for frontend)
- Runs linting (ruff for Python, ESLint for TypeScript)

**Example use**: "Run all tests and make sure they pass"

---

### `/api-codegen`
**When it activates**: Modifying backend routes, schemas, or API endpoints

**What it does**:
- Regenerates TypeScript API client from OpenAPI schema
- Keeps frontend types in sync with backend
- Ensures type safety across the stack

**Example use**: "I added a new endpoint, update the frontend types"

---

### `/email-dev`
**When it activates**: Creating or modifying email templates

**What it does**:
- Starts React Email development server
- Guides through template creation with Tailwind CSS
- Compiles React components to production HTML
- Integrates with backend EmailService

**Example use**: "Create a new password reset email template"

---

### `/docker-health`
**When it activates**: Building Docker images, debugging deployment issues

**What it does**:
- Builds and validates Docker images
- Runs comprehensive health checks
- Troubleshoots container issues
- Verifies production-readiness

**Example use**: "Build the Docker image and make sure it's healthy"

---

### Existing Skills

The project also includes these pre-configured skills:

- `/check-all` - Pre-release checks (type checking, linting, tests)
- `/feature-dev:feature-dev` - Guided feature development
- `/frontend-design:frontend-design` - Frontend interface creation

---

## MCP Servers

MCP (Model Context Protocol) servers provide Claude with access to external tools and data sources.

### Available MCP Servers

#### 1. **Filesystem MCP**
- **Purpose**: Direct file system access
- **When to use**: Large file operations, batch processing
- **Tools available**: Read/write files, list directories, search files

#### 2. **PostgreSQL MCP**
- **Purpose**: Direct database query access
- **When to use**: Schema inspection, complex queries, data analysis
- **Connection**: Uses `DATABASE_URL` or defaults to local dev database
- **Tools available**: Execute SQL, inspect schema, query data

#### 3. **GitHub MCP**
- **Purpose**: GitHub API integration
- **When to use**: PR automation, issue management, repository operations
- **Requires**: `GITHUB_TOKEN` environment variable
- **Tools available**: Create PRs, manage issues, query repositories

### Using MCP Resources

Reference resources with @ mentions:

```
> Can you analyze @github:issue://123?
> What's the schema of @postgres:table://users?
```

### Authenticating MCP Servers

Within Claude Code:

```
> /mcp
```

Follow prompts to authenticate each MCP server.

---

## Automation Hooks

The project includes automatic code formatting and safety checks.

### Auto-Formatting

**Python files** (`.py`):
- Automatically formatted with `ruff format` after edits
- Auto-fixed with `ruff check --fix` for linting issues

**TypeScript/React files** (`.ts`, `.tsx`):
- Automatically formatted with `prettier` after edits

### Safety Blocks

The following files are **blocked** from modification:
- `.env` files (secrets)
- Lock files (`package-lock.json`, `pnpm-lock.yaml`, `uv.lock`)
- `.git/` directory
- `node_modules/`
- `__pycache__/`
- `.terraform/` and `terraform.tfstate`

### User Confirmation Required

You'll be asked to confirm before:
- `git push`
- `git commit`
- `docker compose down`
- Installing new packages (`npm install`, `pnpm add`, `uv add`)
- Creating pull requests

---

## Daily Workflow Examples

### Starting Your Day

```bash
# Navigate to project
cd ~/repos/arive

# Start Claude Code
claude code

# Start development servers
> make dev
```

### Adding a New Feature

**Example**: Adding a new user profile field

```
> I need to add a "bio" field to the user profile. It should be a text field that's optional.

Claude will:
1. Modify the User model in backend/app/models/
2. Create database migration with /db-workflow
3. Apply migration locally
4. Run /api-codegen to update TypeScript types
5. Guide you on frontend changes
6. Run /test-workflow to verify everything works
```

### Fixing a Bug

**Example**: Button not working on dashboard

```
> The "Export Data" button on the dashboard isn't working. Can you investigate and fix it?

Claude will:
1. Find the button component and click handler
2. Trace the API call
3. Check backend route
4. Identify the issue
5. Fix it
6. Run tests to verify the fix
```

### Creating a Pull Request

```
> Create a PR for the changes I just made

Claude will:
1. Review all changes with git diff
2. Run /check-all to ensure everything passes
3. Create a well-formatted PR description
4. Push to remote branch
5. Create PR via GitHub API (if GitHub MCP configured)
```

### Database Operations

**Example**: Adding an index for performance

```
> Users are reporting slow searches. Can you add an index to the email field on the users table?

Claude will:
1. Use /db-workflow skill
2. Create Alembic migration with index
3. Review the migration
4. Apply it locally
5. Verify performance improvement
6. Run tests
```

### Working with Email Templates

**Example**: New welcome email

```
> Create a welcome email template for new users. It should match our design system.

Claude will:
1. Use /email-dev skill
2. Start React Email dev server
3. Create new template in backend/emails/templates/
4. Use Tailwind CSS with brand colors
5. Compile to production HTML
6. Add EmailService method
7. Show you preview at http://localhost:3001
```

---

## Tips for "Vibe Coding"

### 1. Be Conversational

You don't need to be overly technical. Just describe what you want:

❌ "Implement a RESTful CRUD endpoint for the Campaign resource with full validation"
✅ "I need to create, read, update, and delete campaigns via the API"

### 2. Let Claude Guide You

Don't worry about remembering all the commands. Just ask:

```
> I want to test my changes
> I modified the database, what do I do next?
> How do I see the email template I just created?
```

### 3. Ask for Explanations

```
> Why did that test fail?
> What does this error mean?
> Can you explain how RLS policies work?
```

### 4. Iterate Naturally

```
> Actually, can you make that field required instead of optional?
> Let's also add validation for email format
> On second thought, let's use a different color for that button
```

### 5. Use the Skills

The skills are designed to automate complex workflows. Just mention what you're trying to do:

```
> I need to deploy this                    → /docker-health activates
> Let's add a field to the user model      → /db-workflow activates
> The API changed, update the frontend     → /api-codegen activates
> Create a new email                       → /email-dev activates
```

### 6. Leverage MCP Servers

Reference external resources directly:

```
> What does @github:issue://42 say we should do?
> Show me the schema of @postgres:table://campaigns
> Read @filesystem:path://backend/app/config.py
```

### 7. Trust the Automation

The hooks will automatically:
- Format your code (Python with ruff, TypeScript with prettier)
- Block dangerous operations
- Ask for confirmation on important actions

You can focus on the logic, not the formatting.

### 8. Ask for the Big Picture

```
> Give me an overview of how authentication works
> What's the architecture of the email system?
> How do background tasks work in this project?
```

### 9. Combine Operations

```
> Add a new field to the user model, update the API, regenerate the frontend types, and test it all
```

Claude will orchestrate all the steps using the appropriate skills.

### 10. Don't Worry About Mistakes

Claude Code includes safety features:
- Local settings separate from team settings
- Database volumes are persistent (won't lose data)
- Dangerous commands require confirmation
- Auto-formatting prevents style inconsistencies

---

## Troubleshooting

### Claude Code Issues

**Claude won't start**:
```bash
# Check installation
claude --version

# Verify authentication
claude auth login
```

**Skills not loading**:
```bash
# Verify skill files exist
ls -la .claude/skills/

# Check for syntax errors in SKILL.md files
```

**MCP servers not connecting**:
```bash
# List configured servers
claude mcp list

# Check environment variables
echo $GITHUB_TOKEN
echo $DATABASE_URL

# Re-authenticate
# (in Claude Code) /mcp
```

### Development Environment Issues

**Database not starting**:
```bash
# Check Docker is running
docker ps

# Restart database
make db-stop
make db-start

# Check logs
docker logs <container-id>
```

**Port conflicts**:
```bash
# Find what's using port 8000 (backend)
lsof -i :8000

# Find what's using port 3000 (frontend)
lsof -i :3000

# Kill the process if needed
kill -9 <PID>
```

**Dependency issues**:
```bash
# Reinstall everything
make install

# Backend only
cd backend && uv sync

# Frontend only
cd frontend && pnpm install
```

---

## Additional Resources

- **Project Documentation**: See `CLAUDE.md` for architecture overview
- **Backend Guide**: `backend/CLAUDE.md`
- **Frontend Guide**: `frontend/CLAUDE.md`
- **Email Templates**: `backend/emails/CLAUDE.md`
- **Infrastructure**: `infra/CLAUDE.md`
- **Claude Code Docs**: https://code.claude.com/docs

---

## Getting Help

### Within Claude Code

```
> How do I [task]?
> What's the command for [action]?
> Explain [concept] in this codebase
```

### Team Resources

- **Slack**: #engineering channel
- **GitHub Issues**: File issues for bugs or feature requests
- **Team Wiki**: [Link to wiki if applicable]

---

## Next Steps

1. ✅ Complete this setup guide
2. ✅ Run `make dev` to start development servers
3. ✅ Start Claude Code with `claude code`
4. ✅ Try creating a simple feature (e.g., add a field to a model)
5. ✅ Explore the MCP servers with `@` references
6. ✅ Get familiar with the skills by invoking them

Welcome aboard, and happy vibe coding! 🚀
