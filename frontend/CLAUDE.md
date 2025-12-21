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

- **Framework**: Next.js 15 with App Router
- **React**: React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Components**: shadcn/ui (Radix UI primitives)
- **State**: React Query (TanStack Query)
- **API Client**: Auto-generated from OpenAPI schema

### Project Structure

```
frontend/src/
├── app/                    # Next.js App Router pages
│   ├── (authenticated)/   # Authenticated routes
│   ├── (public)/          # Public routes
│   └── layout.tsx         # Root layout
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── data-table/        # Data table system
│   ├── actions/           # Action form components
│   └── ...                # Feature components
├── openapi/               # Auto-generated API client (DO NOT EDIT)
├── lib/                   # Utilities and helpers
└── hooks/                 # Shared React hooks
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

function PostDetailPage({ params }: { params: { id: string } }) {
  const { data } = useOObjectTypeIdGetObjectDetailSuspense('posts', params.id);

  return (
    <ObjectActions
      actions={data.actions}
      actionGroup="post_actions"
      objectId={params.id}
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
'use client';

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
'use client';

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

### 6. Client/Server Components

Next.js App Router uses Server Components by default:

```typescript
// Server Component (default) - can fetch data directly
export default async function PostPage({ params }: { params: { id: string } }) {
  // Can access database or call APIs directly
  return <div>...</div>;
}

// Client Component - use 'use client' directive
'use client';

export default function InteractivePage() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

**When to use Client Components:**

- Need React hooks (useState, useEffect, etc.)
- Event handlers (onClick, onChange, etc.)
- Browser APIs (localStorage, window, etc.)
- Third-party libraries that use hooks

**When to use Server Components:**

- Static content
- Data fetching
- SEO-critical content
- Reduces JavaScript bundle size

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
import { useSearchParams, useRouter } from 'next/navigation';

function PostsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const page = Number(searchParams.get('page') || '1');
  const search = searchParams.get('search') || '';

  const updateSearch = (value: string) => {
    const params = new URLSearchParams(searchParams);
    params.set('search', value);
    router.push(`?${params.toString()}`);
  };

  return <SearchInput value={search} onChange={updateSearch} />;
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

## Routing

### App Router Structure

```
app/
├── (authenticated)/        # Requires login
│   ├── layout.tsx         # Authenticated layout
│   ├── dashboard/         # /dashboard
│   ├── posts/
│   │   ├── page.tsx       # /posts
│   │   └── [id]/
│   │       └── page.tsx   # /posts/[id]
│   └── campaigns/         # /campaigns
└── (public)/              # Public routes
    ├── login/
    └── register/
```

### Navigation

```typescript
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// Link component
<Link href="/posts/123">View Post</Link>

// Programmatic navigation
const router = useRouter();
router.push('/posts');
router.back();
```

### Dynamic Routes

```typescript
// app/(authenticated)/posts/[id]/page.tsx
export default function PostPage({ params }: { params: { id: string } }) {
  const { data } = useOObjectTypeIdGetObjectDetailSuspense('posts', params.id);
  return <div>{data.title}</div>;
}
```

## Error Handling

### Error Boundaries

```typescript
'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
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

1. Create file in `app/(authenticated)/new-feature/page.tsx`
2. Add route to navigation (if needed)
3. Implement using existing patterns
4. Add to sidebar/nav if needed

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

### 1. Use Suspense Boundaries

```typescript
import { Suspense } from 'react';
import { PostsList } from './posts-list';

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <PostsList />
    </Suspense>
  );
}
```

### 2. Lazy Load Components

```typescript
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./heavy-component'), {
  loading: () => <p>Loading...</p>,
});
```

### 3. Optimize Images

```typescript
import Image from 'next/image';

<Image
  src="/photo.jpg"
  alt="Description"
  width={800}
  height={600}
  loading="lazy"
/>
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

### Hydration Errors

Ensure server and client render the same output:

- Don't use browser APIs (localStorage, window) during render
- Use `useEffect` for client-only code
- Use `suppressHydrationWarning` sparingly

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
pnpm install

# Rebuild
pnpm run build
```

## Related Documentation

- [Root Project Guide](/CLAUDE.md) - Overall project architecture
- [Action System Guide](/frontend/ACTION_SYSTEM_GUIDE.md) - Comprehensive action system docs
- [Backend Guide](/backend/CLAUDE.md) - Backend development practices
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [React Query Documentation](https://tanstack.com/query/latest)
