# Email Templates

React Email templates for ManagerLab with live preview and JSON editor.

## Quick Start

```bash
# From project root
make dev-emails

# Or from this directory
npm run dev
```

Visit **http://localhost:3001** to see the email viewer.

## Email Viewer Features

- **📝 Live JSON Editor** (left pane): Edit template data in real-time
- **👀 Live Preview** (right pane): See email rendered with your data
- **🔄 Auto-Compile**: Changes to .tsx files automatically rebuild
- **📑 Template Selector**: Switch between different email templates
- **📱 Mobile View**: Toggle button to hide JSON editor for full-width mobile preview

## Directory Structure

```
emails/
├── templates/           # React Email components
│   ├── _BaseLayout.tsx # Shared layout component
│   ├── _Button.tsx     # Shared button component
│   ├── MagicLink.tsx   # Magic link email
│   └── TeamInvitation.tsx # Team invite email
├── scripts/
│   ├── build.ts        # Compile templates to HTML
│   ├── watch.ts        # Watch for changes
│   └── viewer-server.ts # Dev server for viewer
├── viewer/
│   └── index.html      # Custom email viewer UI
├── design-tokens.ts    # Design system matching frontend
└── package.json
```

## Creating New Templates

1. **Create template file** in `templates/`:
   ```tsx
   // templates/WelcomeEmail.tsx
   import { Heading, Text } from '@react-email/components';
   import { BaseLayout } from './_BaseLayout';
   import { Button } from './_Button';

   interface WelcomeEmailProps {
     user_name: string;
     dashboard_url: string;
   }

   export default function WelcomeEmail({ user_name, dashboard_url }: WelcomeEmailProps) {
     return (
       <BaseLayout preview={`Welcome to Arive, ${user_name}!`}>
         <Heading>Welcome to Arive!</Heading>
         <Text>Hi {user_name}, we're excited to have you.</Text>
         <Button href={dashboard_url}>Go to Dashboard</Button>
       </BaseLayout>
     );
   }
   ```

2. **Update build script** in `scripts/build.ts`:
   ```typescript
   const TEMPLATE_VARIABLES: Record<string, Record<string, string>> = {
     // ... existing templates ...
     'WelcomeEmail': {
       'user_name': '{{ user_name }}',
       'dashboard_url': '{{ dashboard_url }}',
     },
   };
   ```

3. **Update viewer** in `viewer/index.html`:
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

4. **Add EmailService method** in `backend/app/emails/service.py`:
   ```python
   async def send_welcome_email(
       self,
       to_email: str,
       user_name: str,
       dashboard_url: str,
   ) -> str:
       context = {
           "user_name": user_name,
           "dashboard_url": dashboard_url,
       }
       return await self.send_email(
           to=to_email,
           subject="Welcome to Arive!",
           template_name="welcome_email",
           context=context,
       )
   ```

5. **Build and test**:
   ```bash
   npm run build        # Compile to HTML
   npm run dev          # Test in viewer
   ```

## Design System

Templates use design tokens matching the frontend:

- **Primary Color**: `hsl(240 5.9% 10%)` (dark gray, not blue)
- **Font**: Geist Sans
- **Style**: Clean, minimalist shadcn/ui aesthetic

See `design-tokens.ts` for all available colors and spacing values.

## Production Build

Templates are automatically compiled during Docker build:

```dockerfile
# In backend/Dockerfile
RUN cd /app/emails && \
    npm install && \
    npm run build && \
    rm -rf node_modules
```

Compiled HTML files are placed in `backend/templates/emails-react/` with Jinja2 variables ready for runtime substitution.

## Commands

- `npm run dev` - Start viewer with watch mode
- `npm run build` - Compile templates to HTML
- `npm run watch` - Watch for changes and auto-compile
- `npm run viewer-server` - Start viewer server only
- `npm run preview` - Start default React Email preview

## Troubleshooting

**Templates not showing?**
- Make sure you ran `npm run build` at least once
- Check that compiled files exist in `backend/templates/emails-react/`

**Viewer not updating?**
- Check the watch process is running
- Refresh the browser page
- Check console for errors

**Variables not substituting?**
- Verify variable names match between .tsx props and `TEMPLATE_VARIABLES` in `build.ts`
- Check Jinja2 syntax: `{{ variable_name }}`
