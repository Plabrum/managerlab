import { Link } from '@tanstack/react-router';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import { EmptyState } from '@/components/empty-state';
import { Badge } from '@/components/ui/badge';
import {
  CardRow,
  CardRowContent,
  CardRowDescription,
  CardRowLeft,
  CardRowRight,
  CardRowTitle,
} from '@/components/ui/card-row';
import { CardRowList, CardRowListHeader } from '@/components/ui/card-row-list';
import { useActionExecutor } from '@/hooks/use-action-executor';
import { useActionFormRenderer } from '@/hooks/use-action-form-renderer';
import { useListObjectsSuspense } from '@/openapi/objects/objects';
import type {
  ObjectTypes,
  ObjectFilterDefinition,
  ActionDTO,
} from '@/openapi/ariveAPI.schemas';

interface ObjectChildListProps {
  /**
   * The type of child objects to display (e.g., "deliverables")
   */
  objectType: ObjectTypes;
  /**
   * The column name to filter by (e.g., "campaign_id")
   */
  filterColumn: string;
  /**
   * The SQID value to filter by (e.g., parent object's SQID)
   */
  filterValue: string;
  /**
   * Optional parent object's actions for empty state CTA
   */
  parentActions?: ActionDTO[];
  /**
   * Optional parent object's ID for action execution
   */
  parentObjectId?: string;
  /**
   * Optional title for the section (defaults to object type)
   */
  title?: string;
  /**
   * Optional list of field keys to display (defaults to empty - no fields shown)
   * Example: ['platforms', 'posting_date', 'content']
   */
  displayFields?: string[];
  /**
   * Optional callback when a card is clicked
   */
  onCardClick?: (objectId: string) => void;
  /**
   * Optional callback after action completes
   */
  onActionComplete?: () => void;
}

/**
 * ObjectChildList displays a list of child objects as cards, filtered by a parent object.
 * When empty, shows an empty state with a CTA button using the highest priority action
 * from the parent object's actions.
 *
 * Example usage:
 * ```tsx
 * <ObjectChildList
 *   objectType="deliverables"
 *   filterColumn="campaign_id"
 *   filterValue={campaignId}
 *   parentActions={campaign.actions}
 *   parentObjectId={campaignId}
 *   title="Deliverables"
 *   onActionComplete={refetch}
 * />
 * ```
 */
export function ObjectChildList({
  objectType,
  filterColumn,
  filterValue,
  parentActions,
  parentObjectId,
  title,
  displayFields = [],
  onCardClick,
  onActionComplete,
}: ObjectChildListProps) {
  // Build the object filter
  const objectFilter: ObjectFilterDefinition = {
    column: filterColumn,
    values: [filterValue],
    type: 'object_filter',
  };

  // Fetch child objects with filter - request specific columns to get field data
  const { data, refetch } = useListObjectsSuspense(objectType, {
    filters: [objectFilter],
    offset: 0,
    limit: 1000, // Show all items (no pagination as requested)
    column: [], // Request all columns to get field data
  });

  // Default title is the capitalized object type
  const displayTitle =
    title || objectType.charAt(0).toUpperCase() + objectType.slice(1);

  // Get available parent actions (if provided)
  const availableActions = parentActions
    ? parentActions.filter((action) => action.available !== false)
    : [];

  // Get highest priority action (lowest priority number)
  const primaryAction =
    availableActions.length > 0
      ? availableActions.sort(
          (a, b) => (a.priority || 0) - (b.priority || 0)
        )[0]
      : null;

  // Extract action group from primary action
  const actionGroup = primaryAction?.action_group_type;

  // Action executor setup for empty state CTA
  const formRenderer = useActionFormRenderer(undefined);
  const executor = useActionExecutor({
    actionGroup: actionGroup!,
    objectId: parentObjectId, // Parent object's ID for context
    renderActionForm: formRenderer,
    onInvalidate: () => refetch(),
    onSuccess: () => {
      onActionComplete?.();
    },
  });

  // If no children, show empty state
  if (!data.objects || data.objects.length === 0) {
    // Only show empty state if there's a primary action available
    if (!primaryAction) {
      return null;
    }

    return (
      <>
        <EmptyState
          title={`No ${displayTitle.toLowerCase()} added yet`}
          cta={{
            label: primaryAction.label,
            onClick: () => executor.initiateAction(primaryAction),
          }}
          className="rounded-lg border-2 border-dashed py-12"
        />

        <ActionConfirmationDialog
          open={executor.showConfirmation}
          action={executor.pendingAction}
          isExecuting={executor.isExecuting}
          onConfirm={executor.confirmAction}
          onCancel={executor.cancelAction}
        />

        {executor.pendingAction &&
          executor.renderActionForm &&
          executor.renderActionForm({
            action: executor.pendingAction,
            onSubmit: executor.executeWithData,
            onClose: executor.cancelAction,
            isSubmitting: executor.isExecuting,
            isOpen: executor.showForm,
            actionLabel: executor.pendingAction.label,
          })}
      </>
    );
  }

  return (
    <div className="space-y-4">
      <CardRowListHeader title={displayTitle} />

      <div className="max-h-96 overflow-y-auto">
        <CardRowList>
          {data.objects.map((obj) => (
            <CardRow key={obj.id}>
              <CardRowLeft>
                <CardRowContent>
                  <Link
                    to={obj.link || `/${obj.object_type}/${obj.id}`}
                    onClick={() => onCardClick?.(obj.id)}
                    className="block"
                  >
                    <CardRowTitle className="hover:text-primary transition-colors">
                      {obj.title}
                    </CardRowTitle>
                    {obj.subtitle && (
                      <CardRowDescription className="line-clamp-1">
                        {obj.subtitle}
                      </CardRowDescription>
                    )}
                  </Link>
                </CardRowContent>
              </CardRowLeft>

              <CardRowRight>
                {/* Inline fields - show as compact badges/labels */}
                {displayFields.length > 0 &&
                  obj.fields &&
                  obj.fields.length > 0 &&
                  obj.fields
                    .filter((field) => displayFields.includes(field.key))
                    .map((field) => {
                      if (!field.value) return null;

                      // Format the value based on type
                      let displayValue: string;
                      if ('label' in field.value && field.value.label) {
                        displayValue = field.value.label;
                      } else if ('value' in field.value) {
                        const val = field.value.value;
                        if (
                          typeof val === 'string' ||
                          typeof val === 'number'
                        ) {
                          displayValue = String(val);
                        } else if (val instanceof Date) {
                          displayValue = val.toLocaleDateString();
                        } else {
                          displayValue = JSON.stringify(val);
                        }
                      } else {
                        return null;
                      }

                      return (
                        <div
                          key={field.key}
                          className="hidden items-center gap-2 sm:flex"
                        >
                          <span className="text-muted-foreground text-xs">
                            {field.label || field.key}:
                          </span>
                          <Badge
                            variant="outline"
                            className="text-xs font-normal"
                          >
                            {displayValue}
                          </Badge>
                        </div>
                      );
                    })}

                {/* State badge */}
                {obj.state && (
                  <Badge variant="secondary" className="shrink-0 text-xs">
                    {obj.state}
                  </Badge>
                )}
              </CardRowRight>
            </CardRow>
          ))}
        </CardRowList>
      </div>
    </div>
  );
}
