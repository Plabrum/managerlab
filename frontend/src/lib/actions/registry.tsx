import type {
  ActionsActionGroupExecuteActionBody,
  ActionsActionGroupObjectIdExecuteObjectActionBody,
} from '@/openapi/managerLab.schemas';
import type { DomainObject } from '@/types/domain-objects';
import { UpdateDeliverableForm } from '@/components/actions/update-deliverable-form';
import { CreateDeliverableForm } from '@/components/actions/create-deliverable-form';
import { CreateMediaForm } from '@/components/actions/create-media-form';
import { AddMediaToDeliverableForm } from '@/components/actions/add-media-to-deliverable-form';
import { CreateRosterForm } from '@/components/actions/create-roster-form';
import { UpdateRosterForm } from '@/components/actions/update-roster-form';
import { CreateCampaignForm } from '@/components/actions/create-campaign-form';
import { CreateBrandForm } from '@/components/actions/create-brand-form';
import { UpdateBrandForm } from '@/components/actions/update-brand-form';
import React from 'react';

/**
 * Registry entry for an action
 */
export interface ActionRegistryEntry<TData = unknown> {
  /**
   * Render function that returns the form component for this action
   * If returns null, the action will be executed directly without a form
   *
   * @param objectData - Optional object data for extracting default values
   * @param onSubmit - Typed callback that receives the action's data schema
   * @param onCancel - Callback to cancel the action
   * @param isSubmitting - Whether the action is currently submitting
   */
  render: (params: {
    objectData?: DomainObject;
    onSubmit: (data: TData) => void;
    onCancel: () => void;
    isSubmitting: boolean;
  }) => React.ReactElement | null;
}

/**
 * Extract the action type from an action union member
 */
type ExtractActionType<T> = T extends { action: infer A } ? A : never;

/**
 * Extract the data type from an action union member
 */
type ExtractDataType<T> = T extends { data: infer D } ? D : unknown;

/**
 * All possible action types from the discriminated union
 */
export type ActionType = ExtractActionType<
  | ActionsActionGroupExecuteActionBody
  | ActionsActionGroupObjectIdExecuteObjectActionBody
>;

/**
 * Map action type to its data type
 */
export type ActionDataTypeMap = {
  [K in ActionType]: ExtractDataType<
    Extract<
      | ActionsActionGroupExecuteActionBody
      | ActionsActionGroupObjectIdExecuteObjectActionBody,
      { action: K }
    >
  >;
};

/**
 * Type-safe action registry
 * Each key must be a valid action type from the union
 */
export type ActionRegistry = {
  [K in ActionType]?: ActionRegistryEntry<ActionDataTypeMap[K]>;
};

/**
 * Helper to extract field value from object data
 * Handles domain-specific schemas with direct properties
 */
function getFieldValue(objectData: DomainObject, key: string): unknown {
  // Treat as domain-specific schema with direct properties
  return (objectData as unknown as Record<string, unknown>)[key];
}

/**
 * The central action registry
 * This is where all action forms are registered
 *
 * Actions that render null will be executed directly without showing a form
 * Actions not in the registry will also be executed directly
 */
export const actionRegistry: ActionRegistry = {
  // Deliverable actions
  deliverable_actions__deliverable_update: {
    render: ({ objectData, onSubmit, onCancel, isSubmitting }) => {
      // Extract default values from objectData
      const defaultValues = objectData
        ? ({
            title: getFieldValue(objectData, 'title'),
            content: getFieldValue(objectData, 'content'),
            platforms: getFieldValue(objectData, 'platforms'),
            posting_date: getFieldValue(objectData, 'posting_date'),
            notes: getFieldValue(objectData, 'notes'),
            campaign_id: getFieldValue(objectData, 'campaign_id'),
          } as Parameters<typeof onSubmit>[0])
        : undefined;

      return (
        <UpdateDeliverableForm
          defaultValues={defaultValues}
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    },
  },
  top_level_deliverable_actions__top_level_deliverable_create: {
    render: ({ onSubmit, onCancel, isSubmitting }) => {
      return (
        <CreateDeliverableForm
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    },
  },

  // Actions without forms (executed directly)
  deliverable_actions__deliverable_delete: {
    render: () => null,
  },
  deliverable_actions__deliverable_publish: {
    render: () => null,
  },
  deliverable_actions__deliverable_add_media: {
    render: ({ onSubmit, onCancel, isSubmitting }) => {
      return (
        <AddMediaToDeliverableForm
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    },
  },

  // Media actions
  top_level_media_actions__top_level_media_create: {
    render: ({ onSubmit, onCancel, isSubmitting }) => {
      return (
        <CreateMediaForm
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    },
  },

  // Roster actions
  top_level_roster_actions__top_level_roster_create: {
    render: ({ onSubmit, onCancel, isSubmitting }) => {
      return (
        <CreateRosterForm
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    },
  },
  roster_actions__roster_update: {
    render: ({ objectData, onSubmit, onCancel, isSubmitting }) => {
      const defaultValues = objectData
        ? ({
            name: getFieldValue(objectData, 'name'),
            email: getFieldValue(objectData, 'email'),
            phone: getFieldValue(objectData, 'phone'),
            instagram_handle: getFieldValue(objectData, 'instagram_handle'),
            facebook_handle: getFieldValue(objectData, 'facebook_handle'),
            tiktok_handle: getFieldValue(objectData, 'tiktok_handle'),
            youtube_channel: getFieldValue(objectData, 'youtube_channel'),
          } as Parameters<typeof onSubmit>[0])
        : undefined;

      return (
        <UpdateRosterForm
          defaultValues={defaultValues}
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    },
  },
  roster_actions__roster_delete: {
    render: () => null,
  },

  // Campaign actions
  top_level_campaign_actions__campaign_create: {
    render: ({ onSubmit, onCancel, isSubmitting }) => {
      return (
        <CreateCampaignForm
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    },
  },

  // Brand actions
  top_level_brand_actions__brand_create: {
    render: ({ onSubmit, onCancel, isSubmitting }) => {
      return (
        <CreateBrandForm
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    },
  },
  brand_actions__brand_update: {
    render: ({ objectData, onSubmit, onCancel, isSubmitting }) => {
      const defaultValues = objectData
        ? ({
            name: getFieldValue(objectData, 'name'),
            description: getFieldValue(objectData, 'description'),
            website: getFieldValue(objectData, 'website'),
            email: getFieldValue(objectData, 'email'),
            notes: getFieldValue(objectData, 'notes'),
          } as Parameters<typeof onSubmit>[0])
        : undefined;

      return (
        <UpdateBrandForm
          defaultValues={defaultValues}
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    },
  },
  brand_actions__brand_delete: {
    render: () => null,
  },

  // Other action groups can be added here as needed
};

/**
 * Get the render function for a given action type
 */
export function getActionRenderer(
  actionType: ActionType
): ActionRegistryEntry['render'] | undefined {
  const entry = actionRegistry[actionType];
  return entry?.render;
}
