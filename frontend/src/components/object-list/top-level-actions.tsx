import { ObjectActions } from '@/components/object-detail/object-actions';
import { useActionsActionGroupListActionsSuspense } from '@/openapi/actions/actions';
import type { ActionGroupType } from '@/openapi/ariveAPI.schemas';

interface TopLevelActionsProps {
  actionGroup: ActionGroupType;
}

/**
 * Component that fetches and renders top-level actions for an action group.
 * Uses the list_actions endpoint to get available actions without object context.
 */
export function TopLevelActions({ actionGroup }: TopLevelActionsProps) {
  // Fetch available top-level actions
  const { data } = useActionsActionGroupListActionsSuspense(actionGroup);

  // No custom invalidation needed - backend provides invalidate_queries
  // useActionExecutor will handle invalidation automatically

  return (
    <ObjectActions
      actions={data.actions}
      actionGroup={actionGroup}
      // onInvalidate is no longer needed - backend controls invalidation
    />
  );
}
