# Action Registry Guide

## Overview

The centralized action framework provides **one place** to define all action form handling for your typed action union. This eliminates the need for awkward `renderActionForm` callbacks at every callsite.

## Key Benefits

✅ **Type Safety**: TypeScript ensures all action types are handled
✅ **Single Source of Truth**: All action forms defined in one registry
✅ **No Callsite Callbacks**: Clean component interfaces
✅ **Automatic Form Routing**: Forms are automatically shown based on action type
✅ **Easy to Extend**: Add new actions in one place

## Architecture

### 1. Action Registry (`lib/actions/registry.ts`)

The central registry maps action types to their form components:

```typescript
export const actionRegistry: ActionRegistry = {
  deliverable_actions__deliverable_update: {
    FormComponent: UpdateDeliverableActionForm,
  },
  deliverable_actions__deliverable_delete: {
    FormComponent: null, // No form - executes directly
  },
  // ... more actions
};
```

### 2. Form Components (`lib/actions/forms/`)

Form components follow a standardized interface:

```typescript
interface ActionFormProps<TData> {
  defaultValues?: Partial<TData>;
  onSubmit: (data: TData) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}
```

### 3. Hook (`hooks/use-action-form-renderer.tsx`)

The `useActionFormRenderer` hook automatically creates a form renderer from the registry:

```typescript
const renderForm = useActionFormRenderer(getDefaultValues);
```

## Usage

### Basic Usage (No Default Values)

```typescript
// Old way (DEPRECATED)
const renderActionForm = useCallback((props) => {
  if (props.action.action === 'some_action') {
    return <SomeForm {...props} />;
  }
  return null;
}, []);

<ObjectActions
  renderActionForm={renderActionForm} // ❌ No longer needed
/>

// New way (RECOMMENDED)
<ObjectActions
  actions={data.actions}
  actionGroup="deliverable_actions"
  objectId={id}
/>
```

### With Default Values

```typescript
const getDefaultValues = useCallback(
  (action: ActionDTO) => {
    if (action.action === 'deliverable_actions__deliverable_update') {
      return {
        title: data.title,
        content: data.content,
      };
    }
  },
  [data]
);

<ObjectActions
  actions={data.actions}
  actionGroup="deliverable_actions"
  objectId={id}
  getDefaultValues={getDefaultValues}
/>
```

### For List Pages

```typescript
<ActionsMenu
  actions={data.actions}
  actionGroup="top_level_deliverable_actions"
  onActionComplete={() => {
    // Refresh list
  }}
/>
```

## Adding New Actions

### Step 1: Create the Form Component

Create a form in `lib/actions/forms/`:

```typescript
// lib/actions/forms/my-action-form.tsx
export function MyActionForm({
  defaultValues,
  onSubmit,
  onCancel,
  isSubmitting,
}: ActionFormProps<MyActionSchema>) {
  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      onSubmit(formData);
    }}>
      {/* Your form fields */}
    </form>
  );
}
```

### Step 2: Register in the Registry

Add to `lib/actions/registry.ts`:

```typescript
import { MyActionForm } from './forms/my-action-form';

export const actionRegistry: ActionRegistry = {
  // ... existing actions
  my_action_group__my_action: {
    FormComponent: MyActionForm,
  },
};
```

### Step 3: Done!

The form will now automatically appear when the action is triggered. No changes needed at callsites.

## Migration from Old Pattern

### Before (Deliverables Detail Page)

```typescript
// 30+ lines of callback code
const renderDeliverableActionForm: ActionFormRenderer = useCallback(
  (props) => {
    const { action, onSubmit, onCancel, isSubmitting } = props;

    if (action.action === 'deliverable_actions__deliverable_update') {
      const defaultValues = { title: data.title };
      return (
        <UpdateDeliverableForm
          defaultValues={defaultValues}
          onSubmit={(data) => onSubmit({ action: '...', data })}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    }
    return null;
  },
  [data]
);

<ObjectActions renderActionForm={renderDeliverableActionForm} />
```

### After (Deliverables Detail Page)

```typescript
// 8 lines - much cleaner!
const getDefaultValues = useCallback(
  (action: ActionDTO) => {
    if (action.action === 'deliverable_actions__deliverable_update') {
      return { title: data.title };
    }
  },
  [data]
);

<ObjectActions getDefaultValues={getDefaultValues} />
```

## Type Safety Guarantees

The registry ensures:

1. **All action types are handled**: TypeScript knows about the discriminated union
2. **Correct data types**: Each form receives the correct schema type
3. **No missed actions**: If you add a new action to the backend, you'll see it in the registry

## Current Registry Contents

As of now, the following actions are registered:

### Deliverable Actions

- ✅ `deliverable_actions__deliverable_update` → `UpdateDeliverableActionForm`
- ✅ `deliverable_actions__deliverable_delete` → Direct execution (no form)
- ✅ `deliverable_actions__deliverable_publish` → Direct execution (no form)
- ⚠️ `deliverable_actions__deliverable_add_media` → TODO: Add form if needed
- ⚠️ `deliverable_actions__deliverable_remove_media` → TODO: Add form if needed

### Top-Level Deliverable Actions

- ✅ `top_level_deliverable_actions__top_level_deliverable_create` → `CreateDeliverableActionForm`

### Other Action Groups

Add as needed following the same pattern.

## Backward Compatibility

The `renderActionForm` prop is still supported but **deprecated**:

```typescript
interface ObjectActionsProps {
  /**
   * @deprecated Use the centralized action registry instead.
   */
  renderActionForm?: ActionFormRenderer;
}
```

This allows gradual migration. Remove these props once all pages are updated.

## Best Practices

1. **One registry entry per action type** - Keep forms focused
2. **Reuse form components** - Wrap existing forms with the `ActionFormProps` interface
3. **Null for no form** - Set `FormComponent: null` for actions that execute directly
4. **Provide default values** - Use `getDefaultValues` for update/edit actions
5. **Type your schemas** - Leverage the auto-generated OpenAPI types

## FAQ

**Q: What if I need a completely custom form for a specific page?**
A: Use the `renderActionForm` prop (deprecated but still works). However, consider if the form should be in the registry instead.

**Q: How do I handle actions that need different forms in different contexts?**
A: Use the `getDefaultValues` prop to customize the form based on context. The form component stays the same.

**Q: Can I have different triggers (buttons) for actions?**
A: Yes! The registry only controls the form. The trigger is still customizable via the component rendering `ObjectActions` or `ActionsMenu`.

**Q: What about actions with no data (just confirmation)?**
A: Set `FormComponent: null`. The action executor will handle confirmation dialogs automatically if the action has a `confirmation_message`.
