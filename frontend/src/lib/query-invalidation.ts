import type { QueryClient } from '@tanstack/react-query';
import type { ActionDTO, ActionGroupType } from '@/openapi/managerLab.schemas';

/**
 * Map action group to object type for query invalidation
 */
export function actionGroupToObjectType(
  actionGroup: ActionGroupType
): string | null {
  // Map action groups to their corresponding object types
  const mapping: Record<string, string> = {
    media_actions: 'media',
    post_actions: 'posts',
    campaign_actions: 'campaigns',
    brand_actions: 'brands',
    invoice_actions: 'invoices',
    user_actions: 'users',
    brand_contact_actions: 'brandcontacts',
    roster_actions: 'roster',
    top_level_media_actions: 'media',
    top_level_post_actions: 'posts',
    top_level_campaign_actions: 'campaigns',
    top_level_brand_actions: 'brands',
    top_level_invoice_actions: 'invoices',
    top_level_roster_actions: 'roster',
  };

  return mapping[actionGroup] || null;
}

/**
 * Determine if an action modifies data and requires invalidation
 */
export function shouldInvalidateQueries(action: ActionDTO): boolean {
  const actionKey = action.action.toLowerCase();

  // Actions that modify data
  const modifyingActions = [
    'create',
    'update',
    'delete',
    'publish',
    'archive',
    'approve',
    'reject',
  ];

  return modifyingActions.some((verb) => actionKey.includes(verb));
}

/**
 * Smart query invalidation based on action type
 */
export function invalidateQueriesForAction(
  queryClient: QueryClient,
  actionGroup: ActionGroupType,
  objectId: string | undefined,
  action: ActionDTO
): void {
  // Only invalidate for actions that modify data
  if (!shouldInvalidateQueries(action)) {
    return;
  }

  const objectType = actionGroupToObjectType(actionGroup);
  if (!objectType) {
    console.warn(`Unknown action group: ${actionGroup}, skipping invalidation`);
    return;
  }

  const actionKey = action.action.toLowerCase();
  const isDeleteAction = actionKey.includes('delete');
  const isCreateAction = actionKey.includes('create');

  // Always invalidate list queries for this object type
  // This ensures lists are refreshed after create/update/delete
  queryClient.invalidateQueries({
    queryKey: [`/o/${objectType}`],
    refetchType: 'active', // Only refetch currently visible queries
  });

  // For object-specific actions (update, delete), invalidate the detail query
  if (objectId && !isCreateAction) {
    queryClient.invalidateQueries({
      queryKey: [`/o/${objectType}/${objectId}`],
    });
  }

  // For delete actions, we might want to invalidate parent relationships
  if (isDeleteAction) {
    // Invalidate all object queries to ensure parent/child relationships are updated
    queryClient.invalidateQueries({
      queryKey: ['/o/'],
      refetchType: 'active',
    });
  }
}
