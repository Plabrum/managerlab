# Action Registry with Pure Function Extractors

## Overview

The action registry now supports **pure functions** for extracting default values from `ObjectDetailDTO`. This makes it even easier to pre-fill forms with zero configuration at callsites.

## Key Improvement

### Before (Manual Extraction)

```typescript
// Page component - manual extraction needed
const getDefaultValues = useCallback(
  (action: ActionDTO) => {
    if (action.action === 'deliverable_actions__deliverable_update') {
      return {
        title: data.title,
        content: data.fields.find(f => f.key === 'content')?.value,
      };
    }
  },
  [data]
);

<ObjectActions getDefaultValues={getDefaultValues} />
```

### After (Automatic Extraction)

```typescript
// Page component - just pass the data!
<ObjectActions objectData={data} />

// Registry handles extraction automatically:
deliverable_actions__deliverable_update: {
  FormComponent: UpdateDeliverableActionForm,
  extractDefaultValues: (objectData) => ({
    title: objectData.title,
    content: getFieldValue(objectData, 'content'),
  }),
}
```

## Registry Structure

### ActionRegistryEntry Interface

```typescript
export interface ActionRegistryEntry<TData = unknown> {
  /** The form component to render */
  FormComponent: ComponentType<ActionFormProps<TData>> | null;

  /** Pure function to extract default values from object data */
  extractDefaultValues?: (
    objectData: ObjectDetailDTO
  ) => Partial<TData> | undefined;
}
```

### Example Registry Entry

```typescript
export const actionRegistry: ActionRegistry = {
  deliverable_actions__deliverable_update: {
    FormComponent: UpdateDeliverableActionForm,
    extractDefaultValues: (objectData) => {
      // Helper to get field values
      const getFieldValue = (key: string) => {
        const field = objectData.fields.find((f) => f.key === key);
        return field?.value;
      };

      return {
        title: objectData.title,
        content: getFieldValue('content') as string | null | undefined,
        platforms: getFieldValue('platforms') as any,
        posting_date: getFieldValue('posting_date') as string | undefined,
        notes: getFieldValue('notes') as any,
        compensation_structure: getFieldValue('compensation_structure') as any,
        campaign_id: getFieldValue('campaign_id') as number | undefined,
      };
    },
  },
};
```

## Usage Levels

### Level 1: Zero Config (Registry Does Everything)

```typescript
// Most common case - just pass objectData
<ObjectActions
  actions={data.actions}
  actionGroup="deliverable_actions"
  objectId={id}
  objectData={data} // ✅ Registry extracts defaults automatically
/>
```

The registry's `extractDefaultValues` function runs automatically when `objectData` is provided.

### Level 2: Custom Extraction (Override Registry)

```typescript
// Custom logic for specific scenarios
const getDefaultValues = useCallback(
  (action: ActionDTO, objectData?: ObjectDetailDTO) => {
    if (action.action === 'deliverable_actions__deliverable_duplicate') {
      return {
        title: `Copy of ${objectData?.title}`,
        // Custom duplication logic
      };
    }
  },
  []
);

<ObjectActions
  objectData={data}
  getDefaultValues={getDefaultValues} // ✅ Overrides registry
/>
```

Your custom `getDefaultValues` takes **precedence** over the registry's extractor.

### Level 3: No Defaults Needed

```typescript
// Create actions or actions without forms
<ActionsMenu
  actions={data.actions}
  actionGroup="top_level_deliverable_actions"
  // No objectData needed
/>
```

## Adding New Actions with Extractors

### Step 1: Define the Pure Function

```typescript
// In lib/actions/registry.ts
'my_action_group__my_action_update': {
  FormComponent: MyActionForm,
  extractDefaultValues: (objectData) => {
    // Pure function - same input always produces same output
    const getFieldValue = (key: string) =>
      objectData.fields.find((f) => f.key === key)?.value;

    return {
      name: objectData.title,
      description: getFieldValue('description'),
      category: getFieldValue('category'),
    };
  },
}
```

### Step 2: Use at Callsite

```typescript
// Zero config - extractor runs automatically
<ObjectActions objectData={data} />
```

## Best Practices

### 1. Keep Extractors Pure

```typescript
// ✅ GOOD: Pure function
extractDefaultValues: (objectData) => ({
  title: objectData.title,
  status: getFieldValue(objectData, 'status'),
});

// ❌ BAD: Side effects, external dependencies
extractDefaultValues: (objectData) => {
  console.log('Extracting...'); // Side effect!
  const config = fetchConfig(); // External dependency!
  return { title: objectData.title };
};
```

### 2. Helper Functions for Field Extraction

```typescript
// Reusable helper
const getFieldValue = (objectData: ObjectDetailDTO, key: string) => {
  const field = objectData.fields.find((f) => f.key === key);
  return field?.value;
};

// Use in multiple extractors
extractDefaultValues: (objectData) => ({
  field1: getFieldValue(objectData, 'field1'),
  field2: getFieldValue(objectData, 'field2'),
});
```

### 3. Type Casting as Needed

```typescript
extractDefaultValues: (objectData) => ({
  // Cast to the correct type for your schema
  title: objectData.title as string,
  count: getFieldValue(objectData, 'count') as number | undefined,
  status: getFieldValue(objectData, 'status') as 'active' | 'inactive',
});
```

### 4. Only for Update Actions

```typescript
// ✅ Update actions need extractors
'deliverable_actions__deliverable_update': {
  FormComponent: UpdateForm,
  extractDefaultValues: (objectData) => ({ ... }), // Pre-fill form
}

// ✅ Create actions don't need extractors
'deliverable_actions__deliverable_create': {
  FormComponent: CreateForm,
  // No extractDefaultValues - start empty
}

// ✅ Simple actions don't need extractors
'deliverable_actions__deliverable_delete': {
  FormComponent: null, // No form
}
```

## When to Override

Use custom `getDefaultValues` when you need:

1. **Context-specific logic**: Different defaults based on where action is triggered
2. **Complex transformations**: Data needs significant processing
3. **External data**: Defaults depend on data not in `objectData`
4. **Conditional logic**: Different fields based on state/conditions

```typescript
// Example: Conditional defaults
const getDefaultValues = useCallback(
  (action: ActionDTO, objectData?: ObjectDetailDTO) => {
    if (action.action === 'deliverable_actions__deliverable_update') {
      if (userRole === 'admin') {
        return {
          ...registryDefaults,
          admin_notes: 'Admin editing',
        };
      }
    }
  },
  [userRole]
);
```

## Testing Pure Functions

Pure functions are easy to test:

```typescript
import { actionRegistry } from '@/lib/actions/registry';

describe('deliverable_actions__deliverable_update extractor', () => {
  it('extracts title and fields correctly', () => {
    const mockObjectData: ObjectDetailDTO = {
      id: '1',
      title: 'Test Deliverable',
      fields: [
        { key: 'content', value: 'Test content' },
        { key: 'platforms', value: 'instagram' },
      ],
      // ... other required fields
    };

    const extractor =
      actionRegistry.deliverable_actions__deliverable_update
        .extractDefaultValues;

    const result = extractor(mockObjectData);

    expect(result).toEqual({
      title: 'Test Deliverable',
      content: 'Test content',
      platforms: 'instagram',
      // ...
    });
  });
});
```

## Summary

**Before**: Manual extraction at every callsite (8-15 lines)
**After**: Pure function in registry + 1 prop (`objectData`) at callsite

✅ **Testable** - Pure functions are easy to test
✅ **Reusable** - One function used everywhere
✅ **Type-safe** - TypeScript ensures correct types
✅ **Maintainable** - Change in one place
✅ **Discoverable** - All extractors in registry
