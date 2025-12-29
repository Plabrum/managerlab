import { useQueryClient } from '@tanstack/react-query';
import { useMemo } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { toast } from 'sonner';
import {
  KanbanProvider,
  KanbanHeader,
  KanbanCards,
  KanbanCard,
} from '@/components/ui/kanban';
import { getErrorMessage } from '@/lib/error-handler';
import { humanizeEnumValue } from '@/lib/format';
import { useActionsActionGroupObjectIdExecuteObjectAction } from '@/openapi/actions/actions';
import type {
  ObjectListSchema,
  ObjectTypes,
  ObjectFieldDTO,
  ActionGroupType,
  TimeRange,
  ObjectListRequestFiltersItem,
} from '@/openapi/ariveAPI.schemas';
import {
  useListObjectsSuspense,
  useOObjectTypeSchemaGetObjectSchemaSuspense,
} from '@/openapi/objects/objects';

interface ObjectKanbanProps {
  objectType: ObjectTypes;
  searchTerm?: string;
  filters?: ObjectListRequestFiltersItem[];
  timeRange?: TimeRange | null;
  states?: string[]; // Filter which states/columns to show
}

interface KanbanItem extends Record<string, unknown> {
  id: string;
  name: string;
  column: string;
  object: ObjectListSchema;
}

interface KanbanColumn extends Record<string, unknown> {
  id: string;
  name: string;
}

// Map ObjectTypes to ActionGroupType
function getActionGroup(objectType: ObjectTypes): ActionGroupType {
  const mapping: Record<string, ActionGroupType> = {
    deliverables: 'deliverable_actions',
    campaigns: 'campaign_actions',
    invoices: 'invoice_actions',
    media: 'media_actions',
    documents: 'document_actions',
    brands: 'brand_actions',
    deliverable_media: 'deliverable_media_actions',
    roster: 'roster_actions',
    dashboards: 'dashboard_actions',
    widgets: 'widget_actions',
    teams: 'team_actions',
    messages: 'message_actions',
  };
  return mapping[objectType] || 'roster_actions';
}

export function ObjectKanban({
  objectType,
  searchTerm,
  filters = [],
  timeRange,
  states,
}: ObjectKanbanProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Fetch schema to determine state field and available values
  const { data: schema } =
    useOObjectTypeSchemaGetObjectSchemaSuspense(objectType);

  // Find the state column
  const stateColumn = useMemo(() => {
    return schema.columns.find(
      (col) => col.key === 'state' && col.type === 'enum'
    );
  }, [schema.columns]);

  // Build columns from enum values, filtered by states prop if provided
  const columns: KanbanColumn[] = useMemo(() => {
    if (!stateColumn?.available_values) return [];

    const allStates = stateColumn.available_values;
    const statesToShow = states && states.length > 0 ? states : allStates;

    return statesToShow
      .filter((value) => allStates.includes(value)) // Ensure state exists
      .map((value) => ({
        id: value,
        name: humanizeEnumValue(value),
      }));
  }, [stateColumn, states]);

  // Build request filters including time range if specified
  const requestFilters = useMemo(() => {
    const allFilters: ObjectListRequestFiltersItem[] = [...filters];

    // Add time range filter if specified
    if (timeRange) {
      // Time range filtering will be handled by the backend
      // For now, we'll include it as part of the request parameters
    }

    return allFilters;
  }, [filters, timeRange]);

  // Fetch all objects (limit 1000 for kanban view) with filters
  const { data } = useListObjectsSuspense(objectType, {
    offset: 0,
    limit: 1000,
    sorts: [],
    filters: requestFilters,
    search: searchTerm,
  });

  // Transform objects to kanban items
  const items: KanbanItem[] = useMemo(() => {
    return data.objects.map((obj) => {
      // Extract state value from fields
      const stateField = obj.fields?.find((f) => f.key === 'state');
      const stateValue =
        stateField?.value?.type === 'enum'
          ? String(stateField.value.value)
          : columns[0]?.id || 'unknown';

      return {
        id: obj.id,
        name: obj.title,
        column: stateValue,
        object: obj,
      };
    });
  }, [data.objects, columns]);

  // Mutation for updating state
  const executeActionMutation =
    useActionsActionGroupObjectIdExecuteObjectAction();

  // Handle drag end - update object state with optimistic updates
  const handleDataChange = async (updatedData: KanbanItem[]) => {
    // Find what changed
    const changedItems = updatedData.filter((newItem) => {
      const oldItem = items.find((i) => i.id === newItem.id);
      return oldItem && oldItem.column !== newItem.column;
    });

    if (changedItems.length === 0) return;

    // Optimistically update the cache
    const queryKey = ['objects', objectType];
    const previousData = queryClient.getQueryData(queryKey);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    queryClient.setQueryData(queryKey, (old: any) => {
      if (!old) return old;

      return {
        ...old,
        objects: old.objects.map((obj: ObjectListSchema) => {
          const changedItem = changedItems.find((i) => i.id === obj.id);
          if (!changedItem) return obj;

          // Update state field
          return {
            ...obj,
            state: changedItem.column,
            fields: obj.fields?.map((field) => {
              if (field.key === 'state') {
                return {
                  ...field,
                  value: {
                    type: 'enum',
                    value: changedItem.column,
                  },
                };
              }
              return field;
            }),
          };
        }),
      };
    });

    // Execute state updates
    try {
      const actionGroup = getActionGroup(objectType);
      const objectTypeSingular = objectType.endsWith('s')
        ? objectType.slice(0, -1)
        : objectType;

      for (const item of changedItems) {
        const actionBody = {
          action: `${objectTypeSingular}.update_state`,
          data: { new_state: item.column },
        };

        await executeActionMutation.mutateAsync({
          actionGroup,
          objectId: item.id,
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          data: actionBody as any,
        });
      }

      toast.success('Status updated successfully');
    } catch (err) {
      // Rollback on error
      queryClient.setQueryData(queryKey, previousData);
      const errorMessage = getErrorMessage(err, 'Failed to update status');
      toast.error(errorMessage);
    } finally {
      // Invalidate to ensure consistency
      queryClient.invalidateQueries({ queryKey });
    }
  };

  if (!stateColumn) {
    return (
      <div className="text-muted-foreground flex items-center justify-center p-8">
        Kanban view is not available for this object type
      </div>
    );
  }

  return (
    <div className="h-full w-full overflow-hidden">
      <KanbanProvider
        columns={columns}
        data={items}
        onDataChange={handleDataChange}
      >
        {(column) => (
          <div className="bg-muted/50 flex min-w-[220px] flex-col rounded-lg border">
            <KanbanHeader className="border-b p-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <div className="bg-primary h-1.5 w-1.5 rounded-full" />
                  <h3 className="text-sm font-semibold">{column.name}</h3>
                </div>
                <span className="bg-background rounded-full px-1.5 py-0.5 text-xs font-medium">
                  {items.filter((i) => i.column === column.id).length}
                </span>
              </div>
            </KanbanHeader>
            <KanbanCards id={column.id} className="flex-1 space-y-1.5 p-2">
              {(item) => (
                <KanbanCard key={item.id} {...item}>
                  <ObjectKanbanCard object={(item as KanbanItem).object} />
                </KanbanCard>
              )}
            </KanbanCards>
          </div>
        )}
      </KanbanProvider>
    </div>
  );
}

// Card content component
function ObjectKanbanCard({ object }: { object: ObjectListSchema }) {
  const navigate = useNavigate();

  const handleClick = () => {
    // Navigate to object detail page using the link if available
    if (object.link) {
      navigate({ to: object.link });
    }
  };

  return (
    <div
      className="hover:bg-accent/50 -m-1.5 cursor-pointer space-y-1.5 rounded-md p-1.5 transition-colors"
      onClick={handleClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          handleClick();
        }
      }}
      role="button"
      tabIndex={0}
      aria-label={`Open ${object.title}`}
    >
      <div className="line-clamp-2 text-sm font-medium">{object.title}</div>

      {object.subtitle && (
        <div className="text-muted-foreground line-clamp-1 text-xs">
          {object.subtitle}
        </div>
      )}

      {object.fields && object.fields.length > 0 && (
        <div className="space-y-0.5 border-t pt-1 text-xs">
          {object.fields
            .filter((f) => f.key !== 'state')
            .slice(0, 1)
            .map((field) => (
              <div
                key={field.key}
                className="flex justify-between gap-1 truncate"
              >
                <span className="text-muted-foreground truncate">
                  {field.label}:
                </span>
                <span className="truncate font-medium">
                  {formatFieldValue(field)}
                </span>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}

// Helper to format field values
function formatFieldValue(field: ObjectFieldDTO): string {
  if (!field.value) return '-';

  const fieldValue = field.value;

  switch (fieldValue.type) {
    case 'date':
    case 'datetime':
      if ('value' in fieldValue && typeof fieldValue.value === 'string') {
        return new Date(fieldValue.value).toLocaleDateString();
      }
      return '-';
    case 'usd':
      if ('value' in fieldValue && typeof fieldValue.value === 'number') {
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
        }).format(fieldValue.value);
      }
      return '-';
    case 'bool':
      if ('value' in fieldValue && typeof fieldValue.value === 'boolean') {
        return fieldValue.value ? 'Yes' : 'No';
      }
      return '-';
    case 'object':
      if ('label' in fieldValue && 'value' in fieldValue) {
        return fieldValue.label || String(fieldValue.value);
      }
      return '-';
    case 'string':
    case 'text':
    case 'email':
    case 'url':
    case 'enum':
      if ('value' in fieldValue) {
        return String(fieldValue.value || '-');
      }
      return '-';
    case 'int':
    case 'float':
      if ('value' in fieldValue) {
        return String(fieldValue.value || '-');
      }
      return '-';
    case 'image':
      return 'Image';
    default:
      return '-';
  }
}
