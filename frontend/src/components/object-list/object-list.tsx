import {
  useState,
  useEffect,
  useTransition,
  useMemo,
  useCallback,
  useRef,
} from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { toast } from 'sonner';
import { DataTable } from '@/components/data-table/data-table';
import {
  paginationStateToRequest,
  columnFiltersToRequestFilters,
  requestFiltersToColumnFilters,
} from '@/components/data-table/utils';
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
import { useViewModePreference } from '@/hooks/use-view-mode-preference';
import { getActionRenderer, type ActionType } from '@/lib/actions/registry';
import { getErrorMessage } from '@/lib/error-handler';
import { useActionsActionGroupObjectIdExecuteObjectAction } from '@/openapi/actions/actions';
import { SortDirection } from '@/openapi/ariveAPI.schemas';
import {
  useListObjectsSuspense,
  useOObjectTypeSchemaGetObjectSchemaSuspense,
} from '@/openapi/objects/objects';
import { useViewsObjectTypeListSavedViewsSuspense } from '@/openapi/views/views';
import { CardView } from './card-view';
import { GalleryView } from './gallery-view';
import { ObjectListToolbar } from './object-list-toolbar';
import { SavedViewTabs } from './saved-view-tabs';
import type {
  SavedViewConfigSchema,
  ObjectListSchema,
  ObjectTypes,
  ActionDTO,
  ActionsActionGroupObjectIdExecuteObjectActionBody,
} from '@/openapi/ariveAPI.schemas';
import type { DomainObject } from '@/types/domain-objects';
import type {
  SortingState,
  ColumnFiltersState,
  PaginationState,
  Updater,
} from '@tanstack/react-table';

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
  onRowClick,
  onBulkAction,
  currentViewId,
  onViewSelect,
}: ObjectListProps) {
  // Fetch all views (includes system default if user hasn't set a personal default)
  const { data: views } = useViewsObjectTypeListSavedViewsSuspense(objectType);

  // Find selected view in the list, or use first view as default
  // Memoize to prevent unnecessary recalculations
  const currentView = useMemo(() => {
    if (currentViewId !== null && currentViewId !== undefined) {
      // Find by ID (convert to string for comparison since id might be null for system default)
      const found = views.find((v) => String(v.id) === String(currentViewId));
      return found || views[0];
    }
    // Default to first view (backend ensures system default is first if applicable)
    return views[0];
  }, [currentViewId, views]);

  // Get default view mode from preference hook
  const preferenceHook = useViewModePreference(objectType);

  // Single source of truth: unified config state
  const [config, setConfig] = useState<SavedViewConfigSchema>(() => {
    // Initialize from current view or defaults
    if (currentView?.config) {
      return currentView.config;
    }

    return {
      display_mode: preferenceHook.viewMode || 'table',
      column_filters: [],
      column_visibility: {},
      sorting: [],
      search_term: null,
      page_size: pageSize,
      schema_version: 1,
    };
  });

  // Sync initial view selection to parent (on mount only)
  // This ensures the tab is highlighted correctly on page load
  useEffect(() => {
    if (
      onViewSelect &&
      currentView &&
      (currentViewId === null || currentViewId === undefined)
    ) {
      // Parent doesn't know which view is active, tell it
      onViewSelect(currentView.id);
    }
    // Only run on mount when currentViewId is null/undefined
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync config when view ID changes (external state update)
  // This is the ONE effect we need - handles view tab switching
  // Use a ref to track the last view ID we synced from to prevent unnecessary resets
  const lastSyncedViewId = useRef<unknown>(undefined);

  useEffect(() => {
    const viewId = currentView?.id;

    // Only sync if the view ID actually changed (not just object reference)
    if (viewId !== lastSyncedViewId.current) {
      if (currentView?.config) {
        setConfig(currentView.config);
        setPageIndex(0); // Reset pagination when switching views
      }
      lastSyncedViewId.current = viewId;
    }
  }, [currentView]);

  // Transient UI state (not saved in config)
  const [pageIndex, setPageIndex] = useState(0);
  const [isPending, startTransition] = useTransition();
  const [rowSelection, setRowSelection] = useState<Record<string, boolean>>({});

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
  const navigate = useNavigate();

  // Mutation for executing object actions
  const executeObjectActionMutation =
    useActionsActionGroupObjectIdExecuteObjectAction();

  // Fetch schema metadata (cacheable)
  const { data: schema } =
    useOObjectTypeSchemaGetObjectSchemaSuspense(objectType);

  // Config update helper (preserves schema_version)
  const updateConfig = useCallback(
    (updates: Partial<SavedViewConfigSchema>) => {
      setConfig((prev) => ({
        ...prev,
        ...updates,
        schema_version: prev.schema_version,
      }));
    },
    []
  );

  // Detect unsaved changes (simple comparison now!)
  const hasUnsavedChanges = useMemo(() => {
    if (!currentView?.id || !currentView?.config) return false;
    return JSON.stringify(config) !== JSON.stringify(currentView.config);
  }, [currentView, config]);

  // Derive TanStack Table state from config
  const paginationState: PaginationState = {
    pageIndex,
    pageSize: config.page_size || 40,
  };

  // Cast and convert config to typed formats
  const configSorting =
    (config.sorting as unknown as import('@/openapi/ariveAPI.schemas').SortDefinition[]) ||
    [];
  const sortingState: SortingState = configSorting.map((sort) => ({
    id: sort.column,
    desc: sort.direction === SortDirection.sort_desc,
  }));

  // Convert config filters to TanStack format
  const configFilters =
    (config.column_filters as unknown as import('@/openapi/ariveAPI.schemas').ObjectListRequestFiltersItem[]) ||
    [];
  const columnFilters: ColumnFiltersState =
    requestFiltersToColumnFilters(configFilters);

  // Simple update handlers that modify config
  const handlePaginationChange = (updater: Updater<PaginationState>) => {
    startTransition(() => {
      const newState =
        typeof updater === 'function' ? updater(paginationState) : updater;
      setPageIndex(newState.pageIndex);
      updateConfig({ page_size: newState.pageSize });
    });
  };

  const handleSortingChange = (updater: Updater<SortingState>) => {
    startTransition(() => {
      const newState =
        typeof updater === 'function' ? updater(sortingState) : updater;
      updateConfig({
        sorting: newState.map((sort) => ({
          column: sort.id,
          direction: sort.desc
            ? SortDirection.sort_desc
            : SortDirection.sort_asc,
        })) as unknown as typeof config.sorting,
      });
    });
  };

  const handleFiltersChange = (updater: Updater<ColumnFiltersState>) => {
    startTransition(() => {
      const newState =
        typeof updater === 'function' ? updater(columnFilters) : updater;
      updateConfig({
        column_filters: columnFiltersToRequestFilters(
          newState,
          schema.columns
        ) as unknown as typeof config.column_filters,
      });
    });
  };

  const handleSearchChange = (value: string) => {
    startTransition(() => {
      updateConfig({ search_term: value || null });
      setPageIndex(0); // Reset to first page on search
    });
  };

  // Build API request from config
  const { offset, limit } = paginationStateToRequest(paginationState);
  const request = {
    offset,
    limit,
    sorts: configSorting,
    filters: configFilters,
    search:
      config.search_term && config.search_term.trim().length > 0
        ? config.search_term
        : undefined,
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
        navigate({ to: response.action_result.path });
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

  return (
    <div className="container mx-auto flex flex-col gap-2 p-6">
      {/* Tabs - only show if there are multiple views */}
      {views && views.length > 1 && onViewSelect && (
        <SavedViewTabs
          views={views}
          currentViewId={currentViewId}
          onViewSelect={onViewSelect}
        />
      )}

      {/* Unified Toolbar */}
      <ObjectListToolbar
        objectType={objectType}
        columns={schema.columns}
        config={config}
        onSearchChange={handleSearchChange}
        onSortingChange={(sorting) =>
          updateConfig({ sorting: sorting as unknown as typeof config.sorting })
        }
        onFiltersChange={(filters) =>
          updateConfig({
            column_filters: filters as unknown as typeof config.column_filters,
          })
        }
        onViewModeChange={(viewMode) =>
          updateConfig({ display_mode: viewMode })
        }
        onColumnVisibilityChange={(visibility) =>
          updateConfig({ column_visibility: visibility })
        }
        currentView={currentView}
        hasUnsavedChanges={hasUnsavedChanges}
        onViewSelect={onViewSelect}
        enableSearch={enableSearch}
        enableFilters={enableColumnFilters}
        enableSorting={enableSorting}
      />

      {/* Conditional View Rendering */}
      {config.display_mode === 'table' && (
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
          columnVisibility={config.column_visibility || {}}
          onPaginationChange={handlePaginationChange}
          onSortingChange={handleSortingChange}
          onFiltersChange={handleFiltersChange}
          onColumnVisibilityChange={(updater) => {
            const newVisibility =
              typeof updater === 'function'
                ? updater(config.column_visibility || {})
                : updater;
            updateConfig({ column_visibility: newVisibility });
          }}
          onActionClick={handleRowActionClick}
          onBulkActionClick={handleBulkAction}
        />
      )}
      {config.display_mode === 'gallery' && (
        <GalleryView
          data={data.objects}
          columns={schema.columns}
          enableRowSelection={enableRowSelection}
          selectedRows={selectedRowsSet}
          onRowSelectionChange={handleViewSelection}
          onRowClick={onRowClick}
        />
      )}
      {config.display_mode === 'card' && (
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
      {config.display_mode !== 'table' &&
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
