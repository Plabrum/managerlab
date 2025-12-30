# Frontend Development Guide

This guide covers frontend-specific development practices for the Arive platform. For general project information, see the [root CLAUDE.md](/CLAUDE.md).

## Quick Start

```bash
# Install dependencies
make install

# Start development server
make dev-frontend

# Type checking (fast, no build required)
make type-check-frontend

# Linting
make lint-frontend

# Production build
make build-frontend
```

## Architecture Overview

### Tech Stack

- **Build Tool**: Vite (HMR, fast dev server, optimized production builds)
- **Framework**: React 19
- **Router**: TanStack Router (file-based routing)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Components**: shadcn/ui (Radix UI primitives)
- **State**: React Query (TanStack Query)
- **API Client**: Auto-generated from OpenAPI schema

### Project Structure

```
frontend/src/
├── pages/                  # Page components
│   ├── auth/              # Authentication pages
│   ├── campaigns/         # Campaign pages
│   ├── posts/             # Post pages
│   └── dashboard/         # Dashboard pages
├── router/                 # TanStack Router configuration
│   ├── index.tsx          # Router setup
│   ├── root.route.tsx     # Root route
│   ├── authenticated.routes.tsx
│   └── public.routes.tsx
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── data-table/        # Data table system
│   ├── actions/           # Action form components
│   └── ...                # Feature components
├── openapi/               # Auto-generated API client (DO NOT EDIT)
├── lib/                   # Utilities and helpers
├── hooks/                 # Shared React hooks
├── layouts/               # Layout components
└── main.tsx               # Application entry point
```

## Core Patterns

### 1. API Client (Auto-Generated)

The TypeScript API client is auto-generated from the backend OpenAPI schema:

```typescript
import {
  useOObjectTypeGetListObjectsSuspense,
  useActionsActionGroupExecuteActionMutation,
} from '@/openapi/managerLab';

function CampaignsPage() {
  // Auto-generated hook with full type safety
  const { data } = useOObjectTypeGetListObjectsSuspense('campaigns', {
    limit: 40,
    offset: 0,
  });

  return <DataTable data={data.objects} columns={data.columns} />;
}
```

**IMPORTANT:**

- Never edit files in `src/openapi/` - they're auto-generated
- Run `make codegen` after backend schema changes
- All API types are generated from backend msgspec schemas

### 2. Universal Action System

Actions provide a type-safe way to execute operations with automatic UI handling:

```typescript
import { ObjectActions } from '@/components/object-detail';

function PostDetailPage() {
  const { id } = useParams({ from: '/posts/$id' });
  const { data } = useOObjectTypeIdGetObjectDetailSuspense('posts', id);

  return (
    <ObjectActions
      actions={data.actions}
      actionGroup="post_actions"
      objectId={id}
      renderActionForm={renderPostActionForm}  // Optional: for custom forms
    />
  );
}
```

**Action Types:**

- **Simple actions** - Execute immediately (e.g., Publish)
- **Confirmation dialogs** - Auto-shown if backend sets `confirmation_message`
- **Custom forms** - Render via `renderActionForm` callback

**See Also:** [Action System Developer Guide](/frontend/ACTION_SYSTEM_GUIDE.md)

### 3. Custom Action Forms

For actions requiring user input, provide a custom form renderer:

```typescript
import { UpdatePostForm } from '@/components/actions/update-post-form';
import { useCallback } from 'react';

const renderPostActionForm = useCallback(
  (props) => {
    const { action, onSubmit, onCancel, isSubmitting } = props;

    if (action.action === 'post_actions__post_update') {
      return (
        <UpdatePostForm
          defaultValues={data}
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    }

    return null;  // Let system handle other actions
  },
  [data]
);
```

**Form Component Pattern:**

```typescript
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { AppPostsSchemasPostUpdateDTOSchema } from '@/openapi/managerLab.schemas';
import { useState } from 'react';

interface UpdatePostFormProps {
  defaultValues?: Partial<AppPostsSchemasPostUpdateDTOSchema>;
  onSubmit: (data: Record<string, unknown>) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

export function UpdatePostForm({
  defaultValues,
  onSubmit,
  onCancel,
  isSubmitting,
}: UpdatePostFormProps) {
  const [title, setTitle] = useState(defaultValues?.title || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ title, ...otherFields });
  };

  return (
    <form onSubmit={handleSubmit}>
      <Input value={title} onChange={(e) => setTitle(e.target.value)} />
      <Button type="submit" disabled={isSubmitting}>Update</Button>
      <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>
    </form>
  );
}
```

### 4. Data Tables

Display lists of objects with sorting, filtering, pagination:

```typescript
import { DataTable } from '@/components/data-table/data-table';
import { useState } from 'react';

export default function PostsPage() {
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 40 });
  const [sorting, setSorting] = useState([]);
  const [filters, setFilters] = useState([]);

  const { data } = useOObjectTypeGetListObjectsSuspense('posts', {
    limit: pagination.pageSize,
    offset: pagination.pageIndex * pagination.pageSize,
    sorts: sorting,
    filters: filters,
  });

  return (
    <DataTable
      data={data.objects}
      columns={data.columns}
      totalCount={data.total}
      paginationState={pagination}
      sortingState={sorting}
      columnFilters={filters}
      onPaginationChange={setPagination}
      onSortingChange={setSorting}
      onFiltersChange={setFilters}
    />
  );
}
```

### 5. Shadcn/UI Components

Use pre-built components from shadcn/ui:

```bash
# Add new components
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add dialog
pnpm dlx shadcn@latest add form
```

**Available components:** button, dialog, dropdown-menu, input, label, select, table, tabs, and many more.

All components are in `src/components/ui/` and fully customizable.

## Styling with Tailwind CSS

### Tailwind v4 Syntax

This project uses Tailwind CSS v4 with updated syntax:

```tsx
// ✅ Correct (v4)
<div className="bg-neutral-50 text-foreground border">

// ❌ Old (v3)
<div className="bg-gray-50 text-gray-900 border-gray-200">
```

### Design System Colors

Primary color scheme uses dark/neutral grays (NOT blue):

- `bg-background` - Page background
- `bg-card` - Card background
- `text-foreground` - Primary text
- `text-muted-foreground` - Secondary text
- `border` - Border color
- `bg-primary` - Primary action color (dark gray)
- `bg-secondary` - Secondary elements

**See:** `frontend/tailwind.config.ts` for full color palette

### Component Styling Pattern

```tsx
import { cn } from '@/lib/utils';

function Card({ className, ...props }: { className?: string }) {
  return (
    <div
      className={cn(
        'bg-card rounded-lg border p-6 shadow-sm', // Base styles
        className // Allow overrides
      )}
      {...props}
    />
  );
}
```

## Routing with TanStack Router

### Router Structure

TanStack Router uses a file-based routing configuration:

```
src/router/
├── index.tsx                   # Router setup with QueryClient
├── root.route.tsx              # Root layout
├── authenticated.routes.tsx    # Protected routes
├── public.routes.tsx           # Public routes
└── layout.routes.tsx           # Layout routes
```

### Route Configuration

Routes are configured in TypeScript files:

```typescript
// router/authenticated.routes.tsx
import { Route } from '@tanstack/react-router';
import { rootRoute } from './root.route';
import PostsListPage from '@/pages/posts/posts-list-page';
import PostDetailPage from '@/pages/posts/post-detail-page';

// List route
export const postsRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/posts',
  component: PostsListPage,
});

// Detail route with dynamic parameter
export const postDetailRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/posts/$id',
  component: PostDetailPage,
});
```

### Navigation

```typescript
import { Link, useNavigate } from '@tanstack/react-router';

// Link component
<Link to="/posts/$id" params={{ id: '123' }}>
  View Post
</Link>

// Programmatic navigation
const navigate = useNavigate();
navigate({ to: '/posts' });
navigate({ to: '/posts/$id', params: { id: '123' } });
```

### Route Parameters

```typescript
import { useParams } from '@tanstack/react-router';

export default function PostDetailPage() {
  // Type-safe route params
  const { id } = useParams({ from: '/posts/$id' });

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('posts', id);

  return <div>{data.title}</div>;
}
```

### Search Parameters

```typescript
import { useSearch, useNavigate } from '@tanstack/react-router';

function PostsPage() {
  const search = useSearch({ from: '/posts' });
  const navigate = useNavigate();

  const page = search.page || 1;
  const query = search.q || '';

  const updateSearch = (newQuery: string) => {
    navigate({
      to: '/posts',
      search: { ...search, q: newQuery },
    });
  };

  return <SearchInput value={query} onChange={updateSearch} />;
}
```

## State Management

### Server State (API Data)

Use React Query hooks (auto-generated):

```typescript
// Suspense query - throws while loading
const { data } = useOObjectTypeGetListObjectsSuspense('posts', params);

// Regular query - returns loading state
const { data, isLoading, error } = useOObjectTypeGetListObjects(
  'posts',
  params
);

// Mutations
const { mutate } = useActionsActionGroupExecuteActionMutation();
mutate({
  actionGroup: 'post_actions',
  objectId: '123',
  requestBody: { action: 'post_actions__post_publish' },
});
```

#### Caching Strategy

All queries use **automatic scope-based caching** determined by query key patterns. Cache configuration is centralized in `src/lib/cache-config.ts`.

**Cache Scopes:**

- **Session-lifetime (Infinity)**: Metadata that rarely changes
  - Object schemas (`/o/campaigns/schema`)
  - Teams (`/teams`)
  - Dashboards (`/dashboards`)
  - Saved views (`/views/campaigns`)
  - Current user (`/users/current_user`)
- **Data queries (60s)**: User data that changes frequently
  - Object lists (`/o/campaigns`)
  - Object details (`/o/campaigns/123`)
  - Time series data (`/o/campaigns/data`)

**Rules:**

- ✅ Never override `staleTime` in individual queries
- ✅ Use API endpoint patterns in query keys (e.g., `['/o/campaigns']`)
- ✅ Cache invalidation is automatic via the action system
- ✅ Add new patterns to `SESSION_LIFETIME_PATTERNS` in `cache-config.ts`

See [Cache Strategy Guide](./CACHE_STRATEGY.md) for comprehensive documentation.

### Client State

Use React hooks for local state:

```typescript
import { useState } from 'react';

function SearchBar() {
  const [query, setQuery] = useState('');

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
    />
  );
}
```

### URL State (Preferred for Tables)

Use URL search params for sharable state:

```typescript
import { useSearch, useNavigate } from '@tanstack/react-router';

function PostsPage() {
  const search = useSearch({ from: '/posts' });
  const navigate = useNavigate();

  const page = search.page || 1;

  const updatePage = (newPage: number) => {
    navigate({
      to: '/posts',
      search: { ...search, page: newPage },
    });
  };

  return <Pagination page={page} onPageChange={updatePage} />;
}
```

## TypeScript Best Practices

### 1. Import Generated Types

```typescript
import type {
  AppCampaignsSchemasGetCampaignResponseSchema,
  AppPostsSchemasPostUpdateDTOSchema,
} from '@/openapi/managerLab.schemas';
```

### 2. Use Discriminated Unions (Auto-Generated)

Action request bodies are discriminated unions:

```typescript
// Generated from backend
type ActionsActionGroupExecuteActionBody =
  | { action: 'post_actions__post_delete' }
  | { action: 'post_actions__post_update'; data: PostUpdateDTO }
  | { action: 'post_actions__post_publish' };

// TypeScript knows which fields are required based on action
const request: ActionsActionGroupExecuteActionBody = {
  action: 'post_actions__post_update',
  data: { title: 'New Title' }, // data required for update
};
```

### 3. Component Props

```typescript
interface CardProps {
  title: string;
  description?: string;  // Optional
  children?: React.ReactNode;
  className?: string;
}

export function Card({ title, description, children, className }: CardProps) {
  return <div className={className}>...</div>;
}
```

## Error Handling

### Error Boundaries

```typescript
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }: {
  error: Error;
  resetErrorBoundary: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <MyComponent />
    </ErrorBoundary>
  );
}
```

### API Error Handling

```typescript
import { toast } from 'sonner';

const { mutate } = useActionsActionGroupExecuteActionMutation({
  onSuccess: () => {
    toast.success('Action completed successfully');
  },
  onError: (error) => {
    toast.error(error.message || 'Action failed');
  },
});
```

## Testing

### Component Testing

```typescript
import { render, screen } from '@testing-library/react';
import { Button } from '@/components/ui/button';

test('renders button', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByText('Click me')).toBeInTheDocument();
});
```

### Testing with API Mocks

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

test('loads posts', async () => {
  render(
    <QueryClientProvider client={queryClient}>
      <PostsList />
    </QueryClientProvider>
  );

  expect(await screen.findByText('Post Title')).toBeInTheDocument();
});
```

## Common Tasks

### Add a New Page

1. Create page component in `src/pages/feature/feature-page.tsx`
2. Add route in `src/router/authenticated.routes.tsx` or `src/router/public.routes.tsx`
3. Import and register in router tree
4. Add to sidebar/nav if needed

Example:

```typescript
// 1. Create src/pages/reports/reports-page.tsx
export default function ReportsPage() {
  return <div>Reports</div>;
}

// 2. Add to router/authenticated.routes.tsx
import ReportsPage from '@/pages/reports/reports-page';

export const reportsRoute = new Route({
  getParentRoute: () => rootRoute,
  path: '/reports',
  component: ReportsPage,
});

// 3. Register in router tree
const routeTree = rootRoute.addChildren([
  // ... other routes
  reportsRoute,
]);
```

### Add a New shadcn/ui Component

```bash
pnpm dlx shadcn@latest add [component-name]
```

### Update API Client After Backend Changes

```bash
make codegen
```

This regenerates `src/openapi/` with latest schema.

### Add Custom Form for Action

1. Create form component in `components/actions/my-form.tsx`
2. Add `renderActionForm` callback to page
3. Return form component for specific action key
4. See [Action System Guide](/frontend/ACTION_SYSTEM_GUIDE.md) for examples

## Performance Optimization

### 1. Use React.lazy for Code Splitting

```typescript
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./heavy-component'));

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### 2. Optimize Images

```typescript
// Use optimized image formats and lazy loading
<img
  src="/photo.webp"
  alt="Description"
  loading="lazy"
  width={800}
  height={600}
/>
```

### 3. Memoize Expensive Calculations

```typescript
import { useMemo } from 'react';

function DataTable({ data }) {
  const processedData = useMemo(() => {
    return data.map(item => expensiveTransform(item));
  }, [data]);

  return <Table data={processedData} />;
}
```

### 4. Use Vite's Build Optimization

Vite automatically:

- Tree-shakes unused code
- Code-splits dynamic imports
- Optimizes chunk sizes
- Minifies production builds

Configure chunking in `vite.config.ts`:

```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom'],
          'vendor-query': ['@tanstack/react-query'],
        },
      },
    },
  },
});
```

## Code Quality

### Type Checking

```bash
make type-check-frontend  # Fast, no build
```

### Linting

```bash
make lint-frontend  # ESLint
```

### Formatting

```bash
pnpm run format  # Prettier
```

## Troubleshooting

### API Client Type Errors

Run `make codegen` to regenerate after backend changes.

### Build Errors

```bash
# Clear Vite cache
rm -rf node_modules/.vite

# Reinstall dependencies
rm -rf node_modules
pnpm install

# Rebuild
pnpm run build
```

### HMR (Hot Module Replacement) Not Working

- Check that Vite dev server is running on port 3000
- Ensure no conflicting processes on port 3000
- Try restarting the dev server: `make dev-frontend`

### Router Type Errors

TanStack Router generates types automatically. If you see type errors:

1. Ensure routes are properly registered in the router tree
2. Restart TypeScript server in your editor
3. Check that route paths match usage

## Vite-Specific Features

### Environment Variables

Create `.env.local` for local environment variables:

```bash
VITE_API_URL=http://localhost:8000
VITE_FEATURE_FLAG=true
```

Access in code:

```typescript
const apiUrl = import.meta.env.VITE_API_URL;
const isFeatureEnabled = import.meta.env.VITE_FEATURE_FLAG === 'true';
```

### Fast Refresh

Vite's Fast Refresh preserves component state during development:

- Edit components and see changes instantly
- State is preserved across updates
- Automatic when using `.tsx` files

### Development Server Proxy

API calls to `/api` are proxied to backend (configured in `vite.config.ts`):

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

## Related Documentation

- [Root Project Guide](/CLAUDE.md) - Overall project architecture
- [Action System Guide](/frontend/ACTION_SYSTEM_GUIDE.md) - Comprehensive action system docs
- [Backend Guide](/backend/CLAUDE.md) - Backend development practices
- [Vite Documentation](https://vite.dev/)
- [TanStack Router Documentation](https://tanstack.com/router/latest)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [React Query Documentation](https://tanstack.com/query/latest)
