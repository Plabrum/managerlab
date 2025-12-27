'use client';

import {
  useState,
  useEffect,
  useTransition,
  useMemo,
  useCallback,
} from 'react';
import type {
  SortingState,
  ColumnFiltersState,
  PaginationState,
  VisibilityState,
  Updater,
} from '@tanstack/react-table';
import { DataTable } from '@/components/data-table/data-table';
import { DataTableSearch } from '@/components/data-table/data-table-search';
import { DataTableAppliedFilters } from '@/components/data-table/data-table-applied-filters';
import { SavedViewSettings } from './saved-view-settings';
import { SavedViewTabs } from './saved-view-tabs';
import type { SavedViewConfigSchema } from '@/openapi/ariveAPI.schemas';
import { GalleryView } from './gallery-view';
import { CardView } from './card-view';
import { useViewModePreference } from '@/hooks/use-view-mode-preference';
import type { ViewMode } from '@/types/view-modes';
import {
  useListObjectsSuspense,
  useOObjectTypeSchemaGetObjectSchemaSuspense,
} from '@/openapi/objects/objects';
import {
  useViewsObjectTypeListSavedViewsSuspense,
  useViewsObjectTypeDefaultGetDefaultViewSuspense,
} from '@/openapi/views/views';
import {
  sortingStateToSortDefinitions,
  paginationStateToRequest,
  columnFiltersToRequestFilters,
} from '@/components/data-table/utils';
import type {
  ObjectListSchema,
  ObjectTypes,
  ActionDTO,
  ActionsActionGroupObjectIdExecuteObjectActionBody,
} from '@/openapi/ariveAPI.schemas';
import { useActionsActionGroupObjectIdExecuteObjectAction } from '@/openapi/actions/actions';
import { toast } from 'sonner';
import { useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { getErrorMessage } from '@/lib/error-handler';
import { getActionRenderer, type ActionType } from '@/lib/actions/registry';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import type { DomainObject } from '@/types/domain-objects';

interface ObjectListProps {
  objectType: ObjectTypes;
  pageSize?: number;
  enableSearch?: boolean;
  enableRowSelection?: boolean;
  enableSorting?: boolean;
  enableColumnVisibility?: boolean;
  enableColumnFilters?: boolean;
  searchPlaceholder?: string;
  onRowClick?: (row: ObjectListSchema) => void;
  onBulkAction?: (action: string, rows: ObjectListSchema[]) => void;
  // SavedView props (optional for tab switching)
  currentViewId?: unknown | null;
  onViewSelect?: (id: unknown | null) => void;
}

/**
 * ObjectList component - Handles all data table concerns including:
 * - Schema fetching (cached)
 * - State management (pagination, sorting, filtering, search)
 * - Data fetching via useListObjectsSuspense
 * - Rendering search, filters, and table
 *
 * Does NOT include PageTopBar - parent page should wrap this component.
 */
export function ObjectList({
  objectType,
  pageSize = 40,
  enableSearch = true,
  enableRowSelection = true,
  enableSorting = true,
  enableColumnVisibility = true,
  enableColumnFilters = true,
  searchPlaceholder,
  onRowClick,
  onBulkAction,
  currentViewId,
  onViewSelect,
}: ObjectListProps) {
  // Fetch SavedView data internally
  const { data: savedViews } =
    useViewsObjectTypeListSavedViewsSuspense(objectType);
  const { data: defaultView } =
    useViewsObjectTypeDefaultGetDefaultViewSuspense(objectType);

  // Find selected view in the list (all views include full config now)
  const currentView =
    currentViewId !== null && currentViewId !== undefined
      ? savedViews.find((v) => v.id === currentViewId) || defaultView
      : defaultView;
  // Table state
  const [paginationState, setPaginationState] = useState<PaginationState>({
    pageIndex: 0,
    pageSize,
  });
  const [sortingState, setSortingState] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [searchTerm, setSearchTerm] = useState<string | undefined>(undefined);
  const [isPending, startTransition] = useTransition();
  const [rowSelection, setRowSelection] = useState<Record<string, boolean>>({});

  // View mode - managed internally, fallback to preference hook for non-SavedView pages
  const preferenceHook = useViewModePreference(objectType);
  const [viewMode, setViewMode] = useState<ViewMode>(
    (currentView?.config?.display_mode as ViewMode) ||
      preferenceHook.viewMode ||
      'table'
  );

  // Action execution state
  const [pendingAction, setPendingAction] = useState<{
    action: ActionDTO;
    rows: ObjectListSchema[];
  } | null>(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);

  // Query client and router for action handling
  const queryClient = useQueryClient();
  const router = useRouter();

  // Mutation for executing object actions
  const executeObjectActionMutation =
    useActionsActionGroupObjectIdExecuteObjectAction();

  // Fetch schema metadata (cacheable)
  const { data: schema } =
    useOObjectTypeSchemaGetObjectSchemaSuspense(objectType);

  // Reset viewMode and column visibility when switching views (tab change)
  useEffect(() => {
    if (currentView?.config) {
      setViewMode((currentView.config.display_mode as ViewMode) || 'table');
      setColumnVisibility(currentView.config.column_visibility || {});
    }
  }, [currentView?.id, currentView?.config]);

  // Build current config from state
  const currentConfig: SavedViewConfigSchema | undefined = currentView
    ? {
        display_mode: viewMode,
        column_filters: [],
        column_visibility: columnVisibility,
        sorting: [],
        search_term: searchTerm || null,
        page_size: paginationState.pageSize,
        schema_version: 1,
      }
    : undefined;

  // Detect unsaved changes
  const hasUnsavedChanges = useMemo(() => {
    if (!currentView?.id || !currentView?.config) return false;

    // Compare display mode
    if (viewMode !== currentView.config.display_mode) return true;

    // Compare column visibility (deep equality check)
    const savedVisibility = currentView.config.column_visibility || {};
    const currentVisibilityKeys = Object.keys(columnVisibility);
    const savedVisibilityKeys = Object.keys(savedVisibility);

    if (currentVisibilityKeys.length !== savedVisibilityKeys.length)
      return true;

    for (const key of currentVisibilityKeys) {
      if (columnVisibility[key] !== savedVisibility[key]) return true;
    }

    // Compare search term (normalize null/undefined/empty string)
    const savedSearchTerm = currentView.config.search_term || null;
    const currentSearchTerm = searchTerm || null;
    if (currentSearchTerm !== savedSearchTerm) return true;

    // Compare page size
    const savedPageSize = currentView.config.page_size;
    if (
      savedPageSize !== undefined &&
      paginationState.pageSize !== savedPageSize
    )
      return true;

    return false;
  }, [
    currentView,
    viewMode,
    columnVisibility,
    searchTerm,
    paginationState.pageSize,
  ]);

  // Wrap state updates in startTransition to prevent Suspense fallback
  const handlePaginationChange = (updater: Updater<PaginationState>) => {
    startTransition(() => setPaginationState(updater));
  };

  const handleSortingChange = (updater: Updater<SortingState>) => {
    startTransition(() => setSortingState(updater));
  };

  const handleFiltersChange = (updater: Updater<ColumnFiltersState>) => {
    startTransition(() => setColumnFilters(updater));
  };

  const handleSearchChange = (value: string) => {
    startTransition(() => {
      setSearchTerm(value || undefined);
      setPaginationState((prev) => ({ ...prev, pageIndex: 0 }));
    });
  };

  // Build API request
  const { offset, limit } = paginationStateToRequest(paginationState);
  const request = {
    offset,
    limit,
    sorts: sortingStateToSortDefinitions(sortingState),
    filters: columnFiltersToRequestFilters(columnFilters, schema.columns),
    search: searchTerm && searchTerm.trim().length > 0 ? searchTerm : undefined,
  };

  // Fetch data
  const { data } = useListObjectsSuspense(objectType, request);

  // Convert rowSelection to Set for gallery/card views
  const selectedRowsSet = useMemo(
    () => new Set(Object.keys(rowSelection).filter((key) => rowSelection[key])),
    [rowSelection]
  );

  // Handle selection in gallery/card views
  const handleViewSelection = useCallback(
    (rowId: string, selected: boolean) => {
      setRowSelection((prev) => ({ ...prev, [rowId]: selected }));
    },
    []
  );

  // Get selected rows data for bulk actions
  const selectedRowsData = useMemo(
    () => data.objects.filter((obj) => selectedRowsSet.has(obj.id)),
    [data.objects, selectedRowsSet]
  );

  // Get common bulk actions across all selected rows
  const commonBulkActions = useMemo(() => {
    if (selectedRowsData.length === 0) return [];

    const firstRowActions =
      selectedRowsData[0].actions?.filter(
        (action) => action.is_bulk_allowed && action.available !== false
      ) || [];

    return firstRowActions.filter((action) =>
      selectedRowsData.every((row) =>
        row.actions?.some(
          (a) =>
            a.action === action.action &&
            a.is_bulk_allowed &&
            a.available !== false
        )
      )
    );
  }, [selectedRowsData]);

  // Convert ObjectListSchema fields array to a typed object
  // This converts the list view data to a shape compatible with domain objects
  const objectListToPartialDomainObject = (
    obj: ObjectListSchema
  ): Partial<DomainObject> => {
    if (!obj.fields || obj.fields.length === 0) {
      return { id: obj.id };
    }

    // Convert fields array to object with field keys
    // Each field has a nested value structure (e.g., { value: "foo", type: "string" })
    // We extract the actual value from this structure
    const fieldData: Record<string, unknown> = {};
    for (const field of obj.fields) {
      if (
        field.value &&
        typeof field.value === 'object' &&
        'value' in field.value
      ) {
        // Extract the actual value from the field value object
        fieldData[field.key] = field.value.value;
      }
    }

    return {
      id: obj.id,
      ...fieldData,
    } as Partial<DomainObject>;
  };

  // Validate and build action body with proper typing
  const buildActionBody = (
    action: ActionDTO,
    actionData?: unknown
  ): ActionsActionGroupObjectIdExecuteObjectActionBody | null => {
    // The action string comes from the backend and should match the discriminated union
    const actionString = action.action;

    // Check if action is in the registry (basic validation)
    const renderer = getActionRenderer(actionString as ActionType);
    if (renderer === undefined && actionData) {
      console.error('Action not found in registry:', actionString);
      return null;
    }

    // Build the action body
    // We trust the backend's action string since it comes from the API's type system
    // The type assertion is necessary because we're building this dynamically
    return {
      action: actionString,
      data: actionData || {},
    } as ActionsActionGroupObjectIdExecuteObjectActionBody;
  };

  // Execute action with API call
  const executeAction = async (
    action: ActionDTO,
    rows: ObjectListSchema[],
    actionData?: unknown
  ) => {
    setIsExecuting(true);

    try {
      // Determine if this is a bulk action or single row action
      const isBulk = rows.length > 1;
      const row = rows[0];

      // Build and validate action body
      const actionBody = buildActionBody(action, actionData);
      if (!actionBody) {
        throw new Error(`Invalid action: ${action.action}`);
      }

      let response;

      if (isBulk) {
        // For bulk actions, we need to execute the action for each row
        // TODO: Backend should support bulk operations natively
        const promises = rows.map((r) =>
          executeObjectActionMutation.mutateAsync({
            actionGroup: action.action_group_type,
            objectId: r.id,
            data: actionBody,
          })
        );
        const results = await Promise.all(promises);
        response = results[0]; // Use first response for success message
      } else {
        // Single row action
        response = await executeObjectActionMutation.mutateAsync({
          actionGroup: action.action_group_type,
          objectId: row.id,
          data: actionBody,
        });
      }

      // Show success toast
      toast.success(
        response.message || `${action.label} completed successfully`
      );

      // Handle query invalidation
      if (response.invalidate_queries) {
        response.invalidate_queries.forEach((queryKey) => {
          queryClient.invalidateQueries({ queryKey: [queryKey] });
        });
      }

      // Also invalidate the objects list
      queryClient.invalidateQueries({ queryKey: ['objects', objectType] });

      // Handle redirects
      if (response.action_result?.type === 'redirect') {
        router.push(response.action_result.path);
      }

      // Handle downloads
      if (response.action_result?.type === 'download_file') {
        window.open(response.action_result.url, '_blank');
      }

      // Close dialogs
      setShowConfirmation(false);
      setShowForm(false);
      setPendingAction(null);
    } catch (err) {
      const errorMessage = getErrorMessage(
        err,
        `Failed to execute ${action.label}`
      );
      toast.error(errorMessage);
    } finally {
      setIsExecuting(false);
    }
  };

  // Check if action has a custom form
  const hasCustomForm = (action: ActionDTO): boolean => {
    // Cast action.action to ActionType since it comes from the backend as a string
    const renderer = getActionRenderer(action.action as ActionType);
    if (!renderer) return false;

    // Check if renderer returns non-null
    return (
      renderer({
        objectData: undefined,
        onSubmit: () => {},
        onClose: () => {},
        isSubmitting: false,
        isOpen: false,
        actionLabel: action.label,
      }) !== null
    );
  };

  // Initiate an action (single or bulk)
  const initiateAction = (action: ActionDTO, rows: ObjectListSchema[]) => {
    setPendingAction({ action, rows });

    // If action has custom form, show form dialog
    if (hasCustomForm(action)) {
      setShowForm(true);
      return;
    }

    // If action has confirmation message, show confirmation dialog
    if (action.confirmation_message) {
      setShowConfirmation(true);
      return;
    }

    // Execute simple actions directly
    executeAction(action, rows);
  };

  // Row action handler
  const handleRowActionClick = (actionName: string, row: ObjectListSchema) => {
    // Find the action in the row's actions
    const action = row.actions?.find((a) => a.action === actionName);
    if (!action) {
      console.error('Action not found:', actionName);
      return;
    }

    initiateAction(action, [row]);

    // Also call the onRowClick callback if provided
    if (onRowClick) {
      onRowClick(row);
    }
  };

  // Bulk action handler
  const handleBulkAction = (actionName: string, rows: ObjectListSchema[]) => {
    if (rows.length === 0) return;

    // Find the action from the first row (all selected rows should have the same actions)
    const action = rows[0].actions?.find((a) => a.action === actionName);
    if (!action) {
      console.error('Action not found:', actionName);
      return;
    }

    initiateAction(action, rows);

    // Also call the onBulkAction callback if provided
    if (onBulkAction) {
      onBulkAction(actionName, rows);
    }
  };

  // Confirm and execute pending action
  const confirmAction = () => {
    if (pendingAction) {
      executeAction(pendingAction.action, pendingAction.rows);
    }
  };

  // Cancel pending action
  const cancelAction = () => {
    setShowConfirmation(false);
    setShowForm(false);
    setPendingAction(null);
  };

  // Execute action with form data
  const executeWithFormData = (data: unknown) => {
    if (pendingAction) {
      executeAction(pendingAction.action, pendingAction.rows, data);
    }
  };

  const placeholder = searchPlaceholder ?? `Search ${objectType}`;

  return (
    <div className="container mx-auto flex flex-col gap-2 p-6">
      {/* Tabs - only show if there are saved views */}
      {savedViews && savedViews.length > 0 && onViewSelect && (
        <SavedViewTabs
          views={savedViews}
          currentViewId={currentViewId}
          onViewSelect={onViewSelect}
        />
      )}

      {/* Search + Settings */}
      {enableSearch && (
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1">
            <DataTableSearch
              value={searchTerm ?? ''}
              onChangeAction={handleSearchChange}
              placeholder={placeholder}
            />
          </div>
          {currentView && currentConfig && (
            <SavedViewSettings
              objectType={objectType}
              currentView={currentView}
              viewMode={viewMode}
              onViewModeChange={setViewMode}
              hasUnsavedChanges={hasUnsavedChanges}
              currentConfig={currentConfig}
              onViewSelect={onViewSelect}
              columns={schema.columns}
              columnVisibility={columnVisibility}
              onColumnVisibilityChange={setColumnVisibility}
            />
          )}
        </div>
      )}

      {/* Applied Filters */}
      {enableColumnFilters && (
        <DataTableAppliedFilters
          filters={columnFilters}
          columnDefs={schema.columns}
          onUpdate={handleFiltersChange}
        />
      )}

      {/* Conditional View Rendering */}
      {viewMode === 'table' && (
        <DataTable
          isLoading={isPending}
          columns={schema.columns}
          data={data.objects}
          totalCount={data.total}
          enableRowSelection={enableRowSelection}
          enableSorting={enableSorting}
          enableColumnVisibility={enableColumnVisibility}
          enableColumnFilters={enableColumnFilters}
          paginationState={paginationState}
          sortingState={sortingState}
          columnFilters={columnFilters}
          columnVisibility={columnVisibility}
          onPaginationChange={handlePaginationChange}
          onSortingChange={handleSortingChange}
          onFiltersChange={handleFiltersChange}
          onColumnVisibilityChange={setColumnVisibility}
          onActionClick={handleRowActionClick}
          onBulkActionClick={handleBulkAction}
        />
      )}
      {viewMode === 'gallery' && (
        <GalleryView
          data={data.objects}
          columns={schema.columns}
          enableRowSelection={enableRowSelection}
          selectedRows={selectedRowsSet}
          onRowSelectionChange={handleViewSelection}
          onRowClick={onRowClick}
        />
      )}
      {viewMode === 'card' && (
        <CardView
          data={data.objects}
          columns={schema.columns}
          enableRowSelection={enableRowSelection}
          selectedRows={selectedRowsSet}
          onRowSelectionChange={handleViewSelection}
          onRowClick={onRowClick}
        />
      )}

      {/* Bulk Actions Bar (for gallery/card views only - table has its own) */}
      {viewMode !== 'table' &&
        selectedRowsData.length > 0 &&
        commonBulkActions.length > 0 && (
          <div className="bg-muted mt-4 flex items-center justify-between rounded-md border p-3">
            <div className="text-sm font-medium">
              {selectedRowsData.length} of {data.objects.length} row(s) selected
            </div>
            <div className="flex gap-2">
              {commonBulkActions.map((action) => (
                <button
                  key={action.action}
                  type="button"
                  onClick={() => {
                    handleBulkAction(action.action, selectedRowsData);
                    setRowSelection({});
                  }}
                  className="hover:bg-primary/90 bg-primary text-primary-foreground rounded-md px-3 py-1.5 text-sm font-medium"
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>
        )}

      {/* Confirmation Dialog */}
      <AlertDialog open={showConfirmation} onOpenChange={setShowConfirmation}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {pendingAction?.action.label || 'Confirm Action'}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {pendingAction?.action.confirmation_message ||
                'Are you sure you want to perform this action?'}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={cancelAction} disabled={isExecuting}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction onClick={confirmAction} disabled={isExecuting}>
              {isExecuting ? 'Processing...' : 'Continue'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Form Dialog */}
      {showForm &&
        pendingAction &&
        (() => {
          const renderer = getActionRenderer(
            pendingAction.action.action as ActionType
          );
          if (!renderer) return null;

          // Get object data from the first row (for single row actions)
          // Convert ObjectListSchema to partial domain object shape
          // The registry now correctly accepts Partial<DomainObject>, so no type assertion needed
          const partialData =
            pendingAction.rows.length === 1
              ? objectListToPartialDomainObject(pendingAction.rows[0])
              : undefined;

          return renderer({
            objectData: partialData,
            onSubmit: executeWithFormData,
            onClose: cancelAction,
            isSubmitting: isExecuting,
            isOpen: showForm,
            actionLabel: pendingAction.action.label,
          });
        })()}
    </div>
  );
}
