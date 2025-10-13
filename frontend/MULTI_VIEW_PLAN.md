# Multi-View Data Display System - Planning Document

## Overview

This document outlines the plan to extend the current data table component to support multiple view modes: **Table**, **Gallery**, and **Kanban**. The goal is to provide users with flexible ways to visualize and interact with the same dataset depending on their needs.

**Target Views:**

- **Table** (existing) - Traditional row/column data grid
- **Gallery** (new) - Card-based grid layout, ideal for visual content
- **Kanban** (new) - Column-based workflow board with drag-and-drop

---

## Current Architecture

### Existing Components

**DataTable Component** (`frontend/src/components/data-table/data-table.tsx`)

- Built on TanStack Table v8
- Server-side state management (pagination, sorting, filtering)
- Generic data model via `ObjectListDTO[]`
- Dynamic columns via `ColumnDefinitionDTO[]`
- Features: row selection, bulk actions, column visibility, inline filtering
- Action system with row-level and bulk operations

**Data Flow:**

```
Page Component (e.g., posts/page.tsx)
├── State Management (pagination, sorting, filters, search)
├── API Call (useListObjectsSuspense)
├── DataTableSearch
├── DataTableAppliedFilters
└── DataTable
    ├── Column Headers (sortable, filterable)
    ├── Table Body (rows with links)
    ├── Bulk Actions Bar
    └── Pagination Controls
```

**Backend API:**

- Endpoint: `GET /o/{object_type}` (e.g., `/o/posts`, `/o/media`)
- Request: `ObjectListRequest` (limit, offset, sorts, filters, search)
- Response: `ObjectListResponse` (objects, total, columns, actions)

**Key Data Structures:**

```typescript
interface ObjectListDTO {
  id: string;
  object_type: string;
  title: string;
  state: string;
  subtitle?: string;
  actions?: ActionDTO[];
  fields?: ObjectFieldDTO[];
  link?: string;
}

interface ColumnDefinitionDTO {
  key: string;
  label: string;
  type: FieldType; // string, int, bool, date, image, etc.
  filter_type: FilterType;
  sortable?: boolean;
  default_visible?: boolean;
  available_values?: string[];
}
```

---

## Proposed Architecture

### Option 1: Wrapper Component Approach ⭐ **RECOMMENDED**

Create a higher-level orchestrator component that switches between view implementations.

```
DataView (orchestrator)
├── View Mode Selector (toolbar with Table/Kanban/Gallery buttons)
├── Shared Controls (search, filters, actions - rendered outside)
└── View Renderer (conditional based on mode)
    ├── DataTableView (existing table refactored)
    ├── DataGalleryView (new card grid)
    └── DataKanbanView (new board)
```

**Pros:**

- Clean separation of concerns
- Backward compatible (existing pages keep working)
- Progressive rollout (implement views incrementally)
- Each view is independently testable
- Easy to add new views in the future

**Cons:**

- More components to manage
- Need to ensure behavioral consistency
- Some features don't translate across views

### Option 2: Enhanced DataTable with Multiple Renderers

Extend the existing DataTable component to support multiple render modes internally.

**Pros:**

- Single source of truth for state
- Guaranteed consistency
- Less code duplication

**Cons:**

- DataTable becomes very complex
- Harder to customize individual views
- Violates single responsibility principle
- Risk of regression when modifying one view

### Option 3: Composition Pattern

Extract state management into hooks, create standalone presentational components.

**Pros:**

- Maximum flexibility
- Highly reusable pieces
- Best for custom layouts

**Cons:**

- More boilerplate per page
- Less consistency by default
- Steeper learning curve for developers

---

## Recommended Implementation: Wrapper Component Approach

### Component Hierarchy

```typescript
// New wrapper component
<DataView
  objectType="media"
  availableViews={['table', 'gallery']}
  defaultView="gallery"
  data={data}
  columns={columns}
  totalCount={totalCount}
  // ... all other props
/>

// Renders internally:
├── ViewModeSelector (only if availableViews.length > 1)
└── DataTableView | DataGalleryView | DataKanbanView
```

### Shared Interface for View Components

All three view components implement this common interface:

```typescript
interface DataViewComponentProps {
  // Data (same for all views)
  data: ObjectListDTO[];
  columns: ColumnDefinitionDTO[];
  totalCount: number;

  // State management (same for all views)
  paginationState: PaginationState;
  sortingState: SortingState;
  columnFilters: ColumnFiltersState;
  onPaginationChange: OnChangeFn<PaginationState>;
  onSortingChange: OnChangeFn<SortingState>;
  onFiltersChange: OnChangeFn<ColumnFiltersState>;

  // Features (same for all, but may be ignored by some views)
  enableRowSelection?: boolean;
  enableSorting?: boolean;
  isLoading?: boolean;
  onActionClick?: (action: string, row: ObjectListDTO) => void;
  onBulkActionClick?: (action: string, rows: ObjectListDTO[]) => void;

  // View-specific config (optional per view)
  viewConfig?: DataViewConfig;
}

type DataViewConfig = TableViewConfig | GalleryViewConfig | KanbanViewConfig;

interface TableViewConfig {
  type: 'table';
  enableColumnVisibility?: boolean;
  enableColumnFilters?: boolean;
  showItemRange?: boolean;
}

interface GalleryViewConfig {
  type: 'gallery';
  imageField?: string; // Auto-detect from FieldType.image if not specified
  gridColumns?: { sm?: number; md?: number; lg?: number; xl?: number };
  aspectRatio?: 'square' | '16:9' | 'auto';
  cardFields?: string[]; // Which fields to show on cards
}

interface KanbanViewConfig {
  type: 'kanban';
  groupByField: string; // e.g., 'state' - must be an enum field
  cardFields?: string[];
  enableDragDrop?: boolean;
  maxItemsForKanban?: number; // Disable kanban if totalCount exceeds this
  loadAllInKanban?: boolean; // Override pagination when in kanban mode
}
```

### View Mode Persistence

```typescript
// Hook for managing view mode with localStorage persistence
function useViewMode(objectType: string, defaultView: ViewMode = 'table') {
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    const stored = localStorage.getItem(`data-view:${objectType}`);
    return (stored as ViewMode) || defaultView;
  });

  const changeViewMode = (mode: ViewMode) => {
    setViewMode(mode);
    localStorage.setItem(`data-view:${objectType}`, mode);
  };

  return [viewMode, changeViewMode] as const;
}

type ViewMode = 'table' | 'gallery' | 'kanban';
```

---

## View-Specific Constraints & Design

### Gallery View

**Purpose:** Visual card-based grid for image-heavy content (media, products, users with avatars)

**Key Features:**

- Responsive grid layout (2/3/4/6 columns)
- Image field auto-detection or configuration
- Checkbox overlay for selection
- Hover menu for row actions
- Card shows: thumbnail + selected fields

**Image Field Detection Strategy:**

```typescript
// Priority order:
1. Explicit config: galleryConfig.imageField
2. Auto-detect: First field with type === 'image'
3. Fallback: Show icon/placeholder
```

**Card Layout:**

```typescript
<Card>
  <ImageContainer aspectRatio={config.aspectRatio}>
    <Image src={imageUrl} />
    <HoverOverlay>
      <Checkbox /> {/* for selection */}
      <ActionsMenu /> {/* row actions */}
    </HoverOverlay>
  </ImageContainer>
  <CardContent>
    <Title>{item.title}</Title>
    <Subtitle>{item.subtitle}</Subtitle>
    {config.cardFields.map(field => <Field key={field} />)}
  </CardContent>
</Card>
```

**Feature Translation:**

- ✅ Filtering: Yes, affects which cards are shown
- ✅ Sorting: Yes, affects card order
- ✅ Search: Yes, filters cards
- ✅ Row Selection: Yes, via checkbox overlay
- ✅ Bulk Actions: Yes, bottom bar like table
- ✅ Pagination: Yes, traditional or infinite scroll
- ❌ Column Visibility: N/A (shows predefined fields)

**Performance Considerations:**

- Lazy load images with `loading="lazy"`
- Use Intersection Observer for viewport-based loading
- Thumbnail URLs (already in `ImageFieldValue.thumbnail_url`)

### Kanban View

**Purpose:** Workflow visualization with drag-and-drop state management

**Key Features:**

- Vertical columns representing states/stages
- Cards within columns (similar to gallery cards)
- Drag-and-drop between columns
- Scroll within columns
- Group by any enum field

**Column Detection Strategy:**

```typescript
// Determine which field drives columns:
1. Explicit config: kanbanConfig.groupByField
2. Auto-detect: First enum field with filter_type === 'enum_filter'
3. Fallback: Use 'state' field (present in all ObjectListDTO)

// Get column values:
const columnField = columns.find(col => col.key === groupByField);
const columnValues = columnField.available_values || [];
```

**Board Layout:**

```typescript
<KanbanBoard>
  {columnValues.map(columnValue => (
    <KanbanColumn key={columnValue} droppableId={columnValue}>
      <ColumnHeader>{columnValue} ({itemCount})</ColumnHeader>
      <ColumnScroll>
        {items
          .filter(item => item.fields[groupByField] === columnValue)
          .map(item => (
            <DraggableCard draggableId={item.id}>
              <Title>{item.title}</Title>
              <Subtitle>{item.subtitle}</Subtitle>
              {config.cardFields.map(field => <Field />)}
              <ActionsMenu />
            </DraggableCard>
          ))}
      </ColumnScroll>
    </KanbanColumn>
  ))}
</KanbanBoard>
```

**Drag-and-Drop Implementation:**

- Library: `@dnd-kit/core` (modern, accessible, performant)
- On drop: Call backend API to update state
- Optimistic UI: Update local state immediately
- Rollback on error

**Backend API Requirement:**

```typescript
// New endpoint needed:
PATCH /o/{object_type}/{id}/field
{
  field: "state",
  value: "completed"
}

// Or leverage existing action system:
POST /actions/{action_group}/{object_id}/execute
{
  action: "post_actions__update_state",
  data: { state: "completed" }
}
```

**The Pagination Problem 🚨:**

Kanban boards typically show ALL items to visualize the full workflow. However, the current system uses server-side pagination (40 items at a time).

**Options:**

1. **Load All Items in Kanban Mode**
   - Pro: True board experience
   - Con: Performance issue with large datasets
   - Implementation: If `kanbanConfig.loadAllInKanban === true`, fetch all items

2. **Set Maximum Item Threshold**
   - Pro: Prevents performance issues
   - Con: Kanban unavailable for large datasets
   - Implementation: If `totalCount > kanbanConfig.maxItemsForKanban`, disable kanban

3. **Virtual Scrolling per Column**
   - Pro: Handles large datasets
   - Con: Complex to implement with DnD
   - Implementation: Use `@tanstack/react-virtual` within each column

4. **"Load More" per Column**
   - Pro: Progressive loading
   - Con: User can't see full workflow
   - Implementation: Show "Load X more items" button at bottom of each column

**Recommended Strategy:** Combine #1 and #2

- If `totalCount <= 200`: Load all items (pagination.pageSize = 1000)
- If `totalCount > 200`: Disable kanban or show warning

**Feature Translation:**

- ✅ Filtering: Yes, affects which cards are shown
- ⚠️ Sorting: Within columns only (not global)
- ✅ Search: Yes, filters cards across all columns
- ⚠️ Row Selection: Possible but complex across columns
- ⚠️ Bulk Actions: Less intuitive with board layout
- 🚨 Pagination: Conflicts with board concept (see above)

### Shared Concerns

**Feature Parity Matrix:**

| Feature           | Table | Gallery | Kanban | Notes                                      |
| ----------------- | ----- | ------- | ------ | ------------------------------------------ |
| Row Selection     | ✅    | ✅      | ⚠️     | Kanban selection is complex across columns |
| Bulk Actions      | ✅    | ✅      | ⚠️     | Less intuitive in kanban                   |
| Sorting           | ✅    | ✅      | ⚠️     | Kanban sorts within columns only           |
| Filtering         | ✅    | ✅      | ✅     | All views support filtering                |
| Column Visibility | ✅    | ❌      | ❌     | Only table has visible columns             |
| Column Filters    | ✅    | ❌      | ❌     | Only table has per-column filters          |
| Search            | ✅    | ✅      | ✅     | All views support global search            |
| Pagination        | ✅    | ✅      | 🚨     | Kanban conflicts with pagination           |
| Row Actions       | ✅    | ✅      | ✅     | All views support row-level actions        |

**View Availability by Object Type:**

Not all views make sense for all data types. Recommend:

| Object Type | Table        | Gallery      | Kanban |
| ----------- | ------------ | ------------ | ------ |
| media       | ✅           | ✅ (default) | ❌     |
| posts       | ✅ (default) | ⚠️           | ✅     |
| campaigns   | ✅ (default) | ❌           | ✅     |
| invoices    | ✅ (default) | ❌           | ⚠️     |
| users       | ✅ (default) | ✅           | ❌     |
| brands      | ✅ (default) | ❌           | ❌     |

**View Configuration Location:**

Where should view-specific configuration live?

**Option A: Per-Page Configuration** (Recommended)

```typescript
// media/page.tsx
<DataView
  objectType="media"
  availableViews={['table', 'gallery']}
  defaultView="gallery"
  galleryConfig={{
    imageField: 'thumbnail_url',
    aspectRatio: 'square',
    cardFields: ['file_name', 'file_type', 'file_size']
  }}
/>
```

- Pro: Explicit, type-safe, easy to customize per page
- Con: More verbose

**Option B: Auto-Detection**

```typescript
// Gallery automatically finds first field with type === 'image'
// Kanban automatically uses 'state' field
<DataView
  objectType="media"
  availableViews={['table', 'gallery']}
/>
```

- Pro: Less boilerplate
- Con: Magic behavior, harder to override

**Option C: Backend-Driven** (Future)

```typescript
// Backend returns view configuration in ObjectListResponse
interface ObjectListResponse {
  // ... existing fields
  view_configs?: {
    gallery?: GalleryViewConfig;
    kanban?: KanbanViewConfig;
  };
}
```

- Pro: Centralized configuration
- Con: Backend changes required, less flexible

**Recommendation:** Start with **Option A** (per-page config) with sensible defaults that implement **Option B** (auto-detection) behavior when config is not provided.

**View Switching Behavior:**

When user switches views, what happens to state?

| State      | Table → Gallery | Table → Kanban              | Gallery → Kanban   |
| ---------- | --------------- | --------------------------- | ------------------ |
| Pagination | Keep            | Reset to page 1 OR load all | Load all           |
| Sorting    | Keep            | Within-column only          | Within-column only |
| Filters    | Keep            | Keep                        | Keep               |
| Search     | Keep            | Keep                        | Keep               |
| Selection  | Reset           | Reset                       | Reset              |

**Recommendation:** Keep filters and search, reset selection, handle pagination/sorting per view.

---

## Implementation Plan

### Phase 1: Foundation (Week 1)

**Goals:**

- Set up wrapper architecture
- Add view mode switching
- Refactor existing table

**Tasks:**

1. Create `data-view.tsx` wrapper component
2. Create `use-view-mode.ts` hook with localStorage persistence
3. Create `ViewModeSelector` component (toolbar with icons)
4. Refactor `data-table.tsx` → `data-table-view.tsx` (no behavior change)
5. Wire up DataView to render DataTableView
6. Update one page (e.g., `media/page.tsx`) to use DataView as proof-of-concept
7. Verify backward compatibility with other pages

**Deliverables:**

- `frontend/src/components/data-view/data-view.tsx`
- `frontend/src/components/data-view/use-view-mode.ts`
- `frontend/src/components/data-view/view-mode-selector.tsx`
- `frontend/src/components/data-view/data-table-view.tsx` (renamed)
- `frontend/src/components/data-view/types.ts` (shared interfaces)

### Phase 2: Gallery View (Week 2)

**Goals:**

- Implement gallery card grid
- Support image rendering
- Enable selection and actions

**Tasks:**

1. Create `data-gallery-view.tsx` component
2. Implement responsive grid layout (Tailwind grid classes)
3. Create `GalleryCard` component with image, title, fields
4. Add image field auto-detection logic
5. Implement selection checkbox overlay
6. Add hover actions menu
7. Reuse pagination component from table
8. Enable gallery for `media` object type
9. Test with large image sets

**Deliverables:**

- `frontend/src/components/data-view/data-gallery-view.tsx`
- `frontend/src/components/data-view/gallery-card.tsx`
- Updated `media/page.tsx` with gallery as default

### Phase 3: Kanban View (Week 3-4)

**Goals:**

- Implement kanban board layout
- Add drag-and-drop functionality
- Handle pagination constraints

**Tasks:**

1. Install and configure `@dnd-kit/core`
2. Create `data-kanban-view.tsx` component
3. Implement column detection and grouping logic
4. Create `KanbanColumn` component with vertical scroll
5. Create `KanbanCard` component (similar to gallery card)
6. Implement drag-and-drop with optimistic updates
7. Add backend endpoint for state updates (or use action system)
8. Implement "load all" mode when totalCount < threshold
9. Add warning/disable kanban when totalCount > threshold
10. Enable kanban for `posts` and `campaigns` object types
11. Test drag-and-drop across all scenarios

**Deliverables:**

- `frontend/src/components/data-view/data-kanban-view.tsx`
- `frontend/src/components/data-view/kanban-column.tsx`
- `frontend/src/components/data-view/kanban-card.tsx`
- Backend endpoint for state updates (if needed)
- Updated `posts/page.tsx` and `campaigns/page.tsx` with kanban option

### Phase 4: Polish & Documentation (Week 5)

**Goals:**

- Handle edge cases
- Performance optimization
- Documentation

**Tasks:**

1. Add loading states for all views
2. Add empty states for all views
3. Add error boundaries
4. Implement view-specific keyboard shortcuts
5. Add accessibility (ARIA labels, keyboard navigation)
6. Performance audit (lazy loading, virtualization if needed)
7. Write component documentation
8. Create Storybook stories (if using Storybook)
9. Write user-facing documentation
10. Migration guide for updating pages

**Deliverables:**

- Comprehensive component documentation
- User guide for when to use each view
- Migration guide for developers

---

## Migration Strategy

### Backward Compatibility

**Approach:** Gradual opt-in migration

1. **Phase 1:** Both DataTable and DataView coexist
   - Existing pages continue using DataTable (no changes required)
   - New/updated pages can opt into DataView

2. **Phase 2:** DataTable deprecated
   - DataTable becomes thin wrapper around DataView with table-only mode
   - Add deprecation warnings to DataTable
   - Update all pages to use DataView

3. **Phase 3:** DataTable removed
   - Remove DataTable component entirely
   - All pages use DataView

**Example Migration:**

```typescript
// Before (current):
import { DataTable } from '@/components/data-table/data-table';

<DataTable
  columns={data.columns}
  data={data.objects}
  totalCount={data.total}
  // ... props
/>

// After (opt-in):
import { DataView } from '@/components/data-view/data-view';

<DataView
  objectType="media"
  availableViews={['table', 'gallery']}
  defaultView="gallery"
  columns={data.columns}
  data={data.objects}
  totalCount={data.total}
  galleryConfig={{
    aspectRatio: 'square'
  }}
  // ... same props as DataTable
/>

// After (table-only, minimal change):
import { DataView } from '@/components/data-view/data-view';

<DataView
  objectType="media"
  availableViews={['table']}  // Only table, no view switcher shown
  columns={data.columns}
  data={data.objects}
  totalCount={data.total}
  // ... same props as DataTable
/>
```

---

## Open Questions & Design Decisions

### 1. View Configuration Approach

**Decision Needed:** Per-page config vs. auto-detection vs. backend-driven?
**Recommendation:** Start with per-page config (explicit), add auto-detection as fallback
**Rationale:** Balance between flexibility and developer experience

### 2. Kanban Pagination Strategy

**Decision Needed:** Load all vs. max threshold vs. virtual scrolling?
**Recommendation:** Load all if count < 200, disable if count > 200
**Rationale:** Simple to implement, covers most use cases, prevents performance issues

### 3. Search/Filter/Actions Location

**Decision Needed:** Inside DataView or outside (current pattern)?
**Recommendation:** Keep outside (current pattern)
**Rationale:** More flexible, pages already do this, less breaking change

### 4. View Mode Selector Location

**Decision Needed:** Where to show table/gallery/kanban switcher?
**Options:**

- A. Inside DataView header (self-contained)
- B. Outside DataView, page controls it (more flexible)
- C. Configurable position
  **Recommendation:** Inside DataView header (Option A)
  **Rationale:** View mode is core to DataView, keeps component self-contained

### 5. Kanban Backend API

**Decision Needed:** New dedicated endpoint vs. leverage action system?
**Options:**

- A. New endpoint: `PATCH /o/{type}/{id}/field`
- B. Action: `POST /actions/{group}/{id}/execute` with update_state action
- C. Hybrid: Try action system first, fallback to new endpoint
  **Recommendation:** Leverage action system (Option B)
  **Rationale:** Reuse existing infrastructure, consistent with app patterns

### 6. Gallery Card Customization

**Decision Needed:** How flexible should card layouts be?
**Options:**

- A. Fixed layout, only field selection
- B. Multiple preset layouts (compact, detailed, etc.)
- C. Fully customizable with render props
  **Recommendation:** Start with Option A, add Option B later if needed
  **Rationale:** YAGNI principle, can always add flexibility later

### 7. View Availability Rules

**Decision Needed:** How to determine which views are available?
**Options:**

- A. Explicit per page: `availableViews={['table', 'gallery']}`
- B. Backend-driven: API returns available views
- C. Auto-detect: Based on data characteristics (has images → gallery)
  **Recommendation:** Explicit per page (Option A)
  **Rationale:** Clear and predictable, easy to configure

### 8. Mobile Responsiveness

**Decision Needed:** How do views adapt to mobile?
**Considerations:**

- Table: May need horizontal scroll or card fallback
- Gallery: Reduce to 1-2 columns
- Kanban: Horizontal scroll or stack columns?
  **Recommendation:**
  - Table: Keep horizontal scroll (current behavior)
  - Gallery: Responsive grid (2 cols on mobile)
  - Kanban: Horizontal scroll with snap-to-column

---

## Success Criteria

### Functional Requirements

- ✅ Users can switch between table/gallery/kanban views
- ✅ View preference persists in localStorage per object type
- ✅ All views support filtering and search
- ✅ Row/bulk actions work in all applicable views
- ✅ Gallery displays images with proper thumbnails
- ✅ Kanban supports drag-and-drop state changes
- ✅ Backward compatible with existing pages

### Performance Requirements

- ✅ Gallery lazy-loads images
- ✅ Kanban handles up to 200 items smoothly
- ✅ View switching is instant (< 100ms)
- ✅ No performance regression in table view

### Accessibility Requirements

- ✅ All views keyboard-navigable
- ✅ Screen reader support for all interactions
- ✅ ARIA labels for all controls
- ✅ Drag-and-drop has keyboard alternative

### Developer Experience

- ✅ Clear migration path from DataTable to DataView
- ✅ Type-safe component interfaces
- ✅ Comprehensive documentation
- ✅ Easy to add new views in future

---

## Future Enhancements (Out of Scope)

These ideas are deferred to keep initial scope manageable:

1. **Timeline View** - Chronological visualization with date grouping
2. **Calendar View** - For date-based objects (posts, campaigns)
3. **Map View** - Geographic visualization if location data exists
4. **Custom View Templates** - User-defined layouts
5. **View-Specific Filters** - Different filter UIs per view
6. **Saved Views** - User can save custom view configurations
7. **Keyboard Shortcuts** - View-specific hotkeys
8. **Export by View** - Export data in view-specific format
9. **Collaborative Views** - Real-time updates for kanban drag-drop
10. **Advanced Kanban** - Swimlanes, WIP limits, card coloring

---

## References

- TanStack Table Docs: https://tanstack.com/table/v8
- @dnd-kit/core Docs: https://docs.dndkit.com/
- Current DataTable: `frontend/src/components/data-table/data-table.tsx`
- Current Media Gallery: `frontend/src/components/media/media-gallery.tsx`
- Backend API Schemas: `frontend/src/openapi/managerLab.schemas.ts`

---

**Document Version:** 1.0
**Last Updated:** 2025-10-11
**Author:** Planning session with Claude Code
**Status:** Pending Approval
