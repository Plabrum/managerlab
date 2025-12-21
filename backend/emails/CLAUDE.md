# Email Template Development Guide

This guide covers email template development using React Email with Tailwind CSS. For backend-specific info, see [Backend Guide](/backend/CLAUDE.md).

## Quick Start

```bash
# From project root
make dev-emails

# Or from this directory
npm run dev
```

Visit **http://localhost:3001** to see the email viewer with live preview.

## Overview

Email templates are built using React Email, which compiles to production-ready HTML with inline styles. Templates support Jinja2 variables for runtime data substitution.

### Tech Stack
- **React Email** - React components for emails
- **Tailwind CSS** - Utility-first styling (compiled to inline styles)
- **TypeScript** - Type-safe template development
- **Jinja2** - Backend template rendering

### Build Process

```
.tsx templates (Tailwind) → React Email → HTML (inline styles) → Jinja2 variables → Final email
```

## Project Structure

```
emails/
├── templates/              # React Email components (.tsx)
│   ├── _BaseLayout.tsx    # Shared layout wrapper
│   ├── _Button.tsx        # Reusable button component
│   ├── MagicLink.tsx      # Magic link email template
│   └── TeamInvitation.tsx # Team invite template
├── scripts/
│   ├── build.ts           # Compile templates to HTML
│   ├── watch.ts           # Watch mode for development
│   └── viewer-server.ts   # Dev server with JSON editor
├── viewer/
│   └── index.html         # Custom email viewer UI
├── design-tokens.ts       # Design system (colors, spacing)
├── tailwind.config.ts     # Tailwind configuration
└── package.json
```

**Output directory:** `backend/templates/emails-react/` (compiled HTML files)

## Development Workflow

### 1. Start the Email Viewer

```bash
make dev-emails
```

This opens **http://localhost:3001** with:
- 📝 **Live JSON Editor** (left) - Edit template data in real-time
- 👀 **Live Preview** (right) - See rendered email
- 🔄 **Auto-Compile** - Changes auto-rebuild
- 📑 **Template Selector** - Switch between templates
- 📱 **Mobile View** - Toggle for mobile preview

### 2. Create a New Template

**Example: Welcome Email**

```tsx
// templates/WelcomeEmail.tsx
import { Heading, Text } from '@react-email/components';
import { BaseLayout } from './_BaseLayout';
import { Button } from './_Button';

interface WelcomeEmailProps {
  user_name: string;
  dashboard_url: string;
}

export default function WelcomeEmail({
  user_name,
  dashboard_url,
}: WelcomeEmailProps) {
  return (
    <BaseLayout preview={`Welcome to Arive, ${user_name}!`}>
      <Heading className="text-2xl font-bold text-foreground">
        Welcome to Arive!
      </Heading>

      <Text className="text-muted-foreground">
        Hi {user_name}, we're excited to have you on board.
      </Text>

      <Button href={dashboard_url}>Go to Dashboard</Button>

      <Text className="text-sm text-muted-foreground">
        If you have any questions, just reply to this email.
      </Text>
    </BaseLayout>
  );
}
```

**Key Points:**
- Props become Jinja2 variables (e.g., `user_name` → `{{ user_name }}`)
- Use Tailwind classes for styling
- `<BaseLayout>` provides email-safe structure
- Reuse components like `<Button>`

### 3. Register Template Variables

Edit `scripts/build.ts`:

```typescript
const TEMPLATE_VARIABLES: Record<string, Record<string, string>> = {
  // ... existing templates ...

  'WelcomeEmail': {
    'user_name': '{{ user_name }}',
    'dashboard_url': '{{ dashboard_url }}',
  },
};
```

This maps TypeScript props to Jinja2 template variables.

### 4. Add to Email Viewer

Edit `viewer/index.html`:

```javascript
const TEMPLATES = {
  // ... existing templates ...

  'WelcomeEmail': {
    name: 'Welcome Email',
    defaultData: {
      user_name: 'John Doe',
      dashboard_url: 'https://app.tryarive.com/dashboard'
    }
  }
};
```

### 5. Build and Test

```bash
npm run build   # Compile to HTML
npm run dev     # Test in viewer at http://localhost:3001
```

### 6. Add Backend Service Method

Edit `backend/app/emails/service.py`:

```python
async def send_welcome_email(
    self,
    to_email: str,
    user_name: str,
    dashboard_url: str,
) -> str:
    """Send welcome email to new user."""
    context = {
        "user_name": user_name,
        "dashboard_url": dashboard_url,
    }
    return await self.send_email(
        to=to_email,
        subject="Welcome to Arive!",
        template_name="welcome_email",  # Lowercase, no extension
        context=context,
    )
```

### 7. Use in Backend Code

```python
from app.emails import EmailService

email_service = EmailService()
await email_service.send_welcome_email(
    to_email="user@example.com",
    user_name="John Doe",
    dashboard_url="https://app.tryarive.com/dashboard",
)
```

## Design System

### Color Palette

Templates use the same design system as the frontend (dark/neutral grays):

```tsx
// Primary colors (dark gray, not blue!)
<div className="bg-primary text-primary-foreground">Primary Action</div>

// Neutral backgrounds
<div className="bg-neutral-50">Light background</div>
<div className="bg-neutral-900">Dark background</div>

// Semantic colors
<div className="bg-background text-foreground">Page content</div>
<div className="bg-muted text-muted-foreground">Secondary content</div>
<div className="border">Borders</div>
```

**See:** `design-tokens.ts` for full color definitions.

### Typography

```tsx
// Headings
<Heading className="text-2xl font-bold">Main Heading</Heading>
<Heading className="text-xl font-semibold">Sub Heading</Heading>

// Body text
<Text className="text-base">Normal text</Text>
<Text className="text-sm text-muted-foreground">Small text</Text>
```

**Font:** Geist Sans (matches frontend)

### Spacing

Use Tailwind spacing scale:

```tsx
<div className="p-4">Padding 16px</div>
<div className="mb-6">Margin bottom 24px</div>
<div className="space-y-4">Stack with 16px gap</div>
```

## Shared Components

### BaseLayout

Provides email-safe structure and consistent styling:

```tsx
import { BaseLayout } from './_BaseLayout';

<BaseLayout preview="Email subject line preview">
  {/* Your email content */}
</BaseLayout>
```

**Features:**
- Email-safe HTML structure
- Consistent header/footer
- Responsive design
- Preview text support

### Button

Reusable button component with consistent styling:

```tsx
import { Button } from './_Button';

<Button href="https://app.tryarive.com/action">
  Click Here
</Button>
```

**Features:**
- Email-safe button (uses `<a>` tag with button styling)
- Consistent design
- Hover states

## Best Practices

### 1. Use Semantic Tailwind Classes

```tsx
// ✅ Good - Uses semantic design tokens
<div className="bg-background text-foreground border">

// ❌ Avoid - Hard-coded colors
<div style={{ backgroundColor: '#ffffff', color: '#000000' }}>
```

### 2. Test Across Email Clients

Use the email viewer mobile toggle and test in:
- Gmail (web, mobile)
- Outlook (Windows, Mac)
- Apple Mail
- Yahoo Mail

**Tip:** React Email handles most email client quirks automatically.

### 3. Keep Layout Simple

Email clients have limited CSS support:
- Use tables for layout (React Email handles this)
- Avoid complex flexbox/grid
- Inline styles are generated automatically

### 4. Use Preview Text

```tsx
<BaseLayout preview="This text appears in email preview">
  {/* Email content */}
</BaseLayout>
```

### 5. Optimize Images

```tsx
import { Img } from '@react-email/components';

<Img
  src="https://example.com/logo.png"
  alt="Company Logo"
  width="150"
  height="50"
/>
```

**IMPORTANT:**
- Use absolute URLs (not relative paths)
- Specify width/height
- Always include alt text
- Use CDN for hosting images

## Email-Safe HTML

React Email automatically converts modern HTML to email-safe markup:

**Input (React Email):**
```tsx
<div className="flex justify-center bg-neutral-50 p-4 rounded-lg">
  <Button href="https://example.com">Click</Button>
</div>
```

**Output (compiled HTML):**
```html
<table role="presentation" style="background-color: #fafafa; padding: 16px; border-radius: 8px;">
  <tr>
    <td align="center">
      <a href="https://example.com" style="display: inline-block; background-color: #171717; color: #fafafa; padding: 12px 24px; border-radius: 6px; text-decoration: none;">
        Click
      </a>
    </td>
  </tr>
</table>
```

**Key Transformations:**
- `className` → inline `style` attributes
- Flexbox → table layouts
- Modern CSS → email-safe equivalents

## Jinja2 Variables

Props are compiled to Jinja2 variables for runtime substitution:

**Template:**
```tsx
interface Props {
  user_name: string;
  team_name: string;
}

export default function TeamInvite({ user_name, team_name }: Props) {
  return <Text>Hi {user_name}, you've been invited to {team_name}!</Text>;
}
```

**Build Configuration:**
```typescript
// scripts/build.ts
const TEMPLATE_VARIABLES = {
  'TeamInvite': {
    'user_name': '{{ user_name }}',
    'team_name': '{{ team_name }}',
  },
};
```

**Compiled Output:**
```html
<p>Hi {{ user_name }}, you've been invited to {{ team_name }}!</p>
```

**Backend Usage:**
```python
context = {
    "user_name": "John Doe",
    "team_name": "Acme Corp",
}
# Renders: "Hi John Doe, you've been invited to Acme Corp!"
```

## Production Build

### Manual Build

```bash
npm run build
```

Compiled templates go to `backend/templates/emails-react/`.

### Docker Build

Templates are automatically built during Docker image creation:

```dockerfile
# In backend/Dockerfile
COPY emails ./emails
RUN cd /app/emails && \
    npm install && \
    npm run build && \
    rm -rf node_modules
```

**IMPORTANT:** Compiled templates must be committed to Git and included in the Docker image. The build process does not run in production - only at Docker build time.

## Commands

```bash
npm run dev              # Start viewer with watch mode (http://localhost:3001)
npm run build            # Compile templates to HTML
npm run watch            # Watch for changes and auto-compile
npm run viewer-server    # Start viewer server only
npm run preview          # Start default React Email preview
```

## Troubleshooting

### Templates not showing in viewer?

1. Make sure you ran `npm run build` at least once
2. Check that compiled files exist in `backend/templates/emails-react/`
3. Restart the viewer server

### Viewer not updating?

1. Check the watch process is running
2. Refresh the browser
3. Check console for compilation errors

### Variables not substituting?

1. Verify variable names match between `.tsx` props and `TEMPLATE_VARIABLES` in `build.ts`
2. Check Jinja2 syntax: `{{ variable_name }}`
3. Ensure backend context dict has the correct keys

### Styles not applying?

1. Tailwind config should match frontend config
2. Check that `<Tailwind>` component wraps content (included in `BaseLayout`)
3. Run `npm run build` to recompile

### Images not loading?

1. Use absolute URLs (not relative paths)
2. Ensure images are publicly accessible
3. Check CORS settings if hosted on CDN

## Testing Emails

### Local Testing (Development)

Use the email viewer at http://localhost:3001 to preview templates with test data.

### Sending Test Emails

```python
from app.emails import EmailService

# In development, emails may print to console or use test SMTP
email_service = EmailService()
await email_service.send_welcome_email(
    to_email="your-email@example.com",
    user_name="Test User",
    dashboard_url="https://app.tryarive.com",
)
```

### Email Client Testing

Use services like [Litmus](https://litmus.com/) or [Email on Acid](https://www.emailonacid.com/) for comprehensive testing across email clients.

## Migration from Old Templates

If migrating from plain HTML templates:

1. Create new `.tsx` file in `templates/`
2. Convert HTML to React Email components
3. Replace inline styles with Tailwind classes
4. Add to `TEMPLATE_VARIABLES` in `build.ts`
5. Add to viewer in `viewer/index.html`
6. Build and test
7. Update backend `EmailService` to use new template name

## Related Documentation

- [Backend Guide](/backend/CLAUDE.md) - Backend development practices
- [Root Project Guide](/CLAUDE.md) - Overall architecture
- [React Email Documentation](https://react.email/docs/introduction)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## External Resources

- [React Email Components](https://react.email/docs/components/html)
- [Email Client CSS Support](https://www.caniemail.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
