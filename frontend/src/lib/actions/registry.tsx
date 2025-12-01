import type {
  ActionsActionGroupExecuteActionBody,
  ActionsActionGroupObjectIdExecuteObjectActionBody,
  CampaignSchema,
  BrandSchema,
  DeliverableResponseSchema,
  MediaResponseSchema,
  RosterSchema,
  InvoiceSchema,
  TeamSchema,
  DashboardSchema,
  WidgetSchema,
} from '@/openapi/ariveAPI.schemas';
import type { DomainObject } from '@/types/domain-objects';
import { UpdateDeliverableForm } from '@/components/actions/update-deliverable-form';
import { CreateDeliverableForm } from '@/components/actions/create-deliverable-form';
import { CreateMediaForm } from '@/components/actions/create-media-form';
import { AddMediaToDeliverableForm } from '@/components/actions/add-media-to-deliverable-form';
import { CreateRosterForm } from '@/components/actions/create-roster-form';
import { UpdateRosterForm } from '@/components/actions/update-roster-form';
import { CreateCampaignForm } from '@/components/actions/create-campaign-form';
import { UpdateCampaignForm } from '@/components/actions/update-campaign-form';
import { CreateBrandForm } from '@/components/actions/create-brand-form';
import { UpdateBrandForm } from '@/components/actions/update-brand-form';
import { AddDeliverableToCampaignForm } from '@/components/actions/add-deliverable-to-campaign-form';
import { InviteUserToTeamForm } from '@/components/actions/invite-user-to-team-form';
import { CreateDashboardForm } from '@/components/actions/create-dashboard-form';
import { UpdateDashboardForm } from '@/components/actions/update-dashboard-form';
import { UpdateWidgetForm } from '@/components/dashboard/update-widget-form';
import React from 'react';

/**
 * Registry entry for an action
 * @template TData - The data type for the action (from the action's data field)
 * @template TObject - The object type this action operates on (e.g., CampaignSchema, BrandSchema)
 */
export interface ActionRegistryEntry<TData = unknown, TObject = DomainObject> {
  /**
   * Render function that returns the self-contained modal form component for this action
   * If returns null, the action will be executed directly without a form
   *
   * @param objectData - Optional object data, strongly typed to the action's object type
   * @param onSubmit - Typed callback that receives the action's data schema
   * @param onClose - Callback to close the modal
   * @param isSubmitting - Whether the action is currently submitting
   * @param isOpen - Whether the modal should be open
   * @param actionLabel - The label/title for the action
   */
  render: (params: {
    objectData?: TObject;
    onSubmit: (data: TData) => void;
    onClose: () => void;
    isSubmitting: boolean;
    isOpen: boolean;
    actionLabel: string;
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
 * Map action keys to their corresponding object types
 * This provides compile-time type safety for objectData in each action
 */
export type ActionToObjectMap = {
  // Campaign actions
  campaign_actions__campaign_update: CampaignSchema;
  campaign_actions__campaign_delete: CampaignSchema;
  campaign_actions__campaign_add_deliverable: CampaignSchema;
  campaign_actions__campaign_create: never; // Top-level, no object

  // Brand actions
  brand_actions__brand_update: BrandSchema;
  brand_actions__brand_delete: BrandSchema;
  brand_actions__brand_create: never;

  // Deliverable actions
  deliverable_actions__deliverable_update: DeliverableResponseSchema;
  deliverable_actions__deliverable_delete: DeliverableResponseSchema;
  deliverable_actions__deliverable_publish: DeliverableResponseSchema;
  deliverable_actions__deliverable_add_media: DeliverableResponseSchema;
  deliverable_actions__deliverable_create: never;

  // Media actions
  media_actions__media_update: MediaResponseSchema;
  media_actions__media_delete: MediaResponseSchema;
  media_actions__media_download: MediaResponseSchema;
  media_actions__media_register: never;

  // Roster actions
  roster_actions__roster_update: RosterSchema;
  roster_actions__roster_delete: RosterSchema;
  roster_actions__roster_create: never;

  // Invoice actions
  invoice_actions__invoice_update: InvoiceSchema;
  invoice_actions__invoice_delete: InvoiceSchema;
  invoice_actions__invoice_create: never;

  // Deliverable media actions
  deliverable_media_actions__deliverable_media_accept: never; // No object, operates on association
  deliverable_media_actions__deliverable_media_reject: never;
  deliverable_media_actions__deliverable_media_remove_media: never;

  // Dashboard actions
  dashboard_actions__create: never; // Top-level action
  dashboard_actions__edit: DashboardSchema;
  dashboard_actions__delete: DashboardSchema;
  dashboard_actions__update: DashboardSchema;

  // Widget actions
  widget_actions__create: never; // Top-level action
  widget_actions__update: WidgetSchema;
  widget_actions__delete: WidgetSchema;

  // Team actions
  team_actions__team_delete: TeamSchema;
  team_actions__team_invite_user: TeamSchema;

  // Message actions
  message_actions__delete: never;
  message_actions__update: never;

  // Document actions
  document_actions__document_update: never;
  document_actions__document_delete: never;
  document_actions__document_download: never;
  document_actions__document_register: never;

  // Campaign contract actions
  campaign_actions__campaign_add_contract: never;
  campaign_actions__campaign_replace_contract: never;
};

/**
 * Type-safe action registry
 * Each key must be a valid action type from the union
 * Object data is strongly typed based on the action's object type
 */
export type ActionRegistry = {
  [K in ActionType]: ActionRegistryEntry<
    ActionDataTypeMap[K],
    K extends keyof ActionToObjectMap ? ActionToObjectMap[K] : DomainObject
  >;
};

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
    render: ({
      objectData,
      onSubmit,
      onClose,
      isSubmitting,
      isOpen,
      actionLabel,
    }) => {
      // objectData is typed as DeliverableResponseSchema | undefined
      return (
        <UpdateDeliverableForm
          isOpen={isOpen}
          onClose={onClose}
          defaultValues={objectData}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },
  deliverable_actions__deliverable_create: {
    render: ({ onSubmit, onClose, isSubmitting, isOpen, actionLabel }) => {
      return (
        <CreateDeliverableForm
          isOpen={isOpen}
          onClose={onClose}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
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
    render: ({ onSubmit, onClose, isSubmitting, isOpen, actionLabel }) => {
      return (
        <AddMediaToDeliverableForm
          isOpen={isOpen}
          onClose={onClose}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },

  // Media actions
  media_actions__media_register: {
    render: ({ onSubmit, onClose, isSubmitting, isOpen, actionLabel }) => {
      return (
        <CreateMediaForm
          isOpen={isOpen}
          onClose={onClose}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },

  // Roster actions
  roster_actions__roster_create: {
    render: ({ onSubmit, onClose, isSubmitting, isOpen, actionLabel }) => {
      return (
        <CreateRosterForm
          isOpen={isOpen}
          onClose={onClose}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },
  roster_actions__roster_update: {
    render: ({
      objectData,
      onSubmit,
      onClose,
      isSubmitting,
      isOpen,
      actionLabel,
    }) => {
      // objectData is typed as RosterSchema | undefined
      return (
        <UpdateRosterForm
          isOpen={isOpen}
          onClose={onClose}
          defaultValues={objectData}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },
  roster_actions__roster_delete: {
    render: () => null,
  },

  // Campaign actions
  campaign_actions__campaign_create: {
    render: ({ onSubmit, onClose, isSubmitting, isOpen, actionLabel }) => {
      return (
        <CreateCampaignForm
          isOpen={isOpen}
          onClose={onClose}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },
  campaign_actions__campaign_add_deliverable: {
    render: ({ onSubmit, onClose, isSubmitting, isOpen, actionLabel }) => {
      return (
        <AddDeliverableToCampaignForm
          isOpen={isOpen}
          onClose={onClose}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },
  campaign_actions__campaign_update: {
    render: ({
      objectData,
      onSubmit,
      onClose,
      isSubmitting,
      isOpen,
      actionLabel,
    }) => {
      // objectData is typed as CampaignSchema | undefined
      return (
        <UpdateCampaignForm
          isOpen={isOpen}
          onClose={onClose}
          defaultValues={objectData}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },
  campaign_actions__campaign_delete: {
    render: () => null,
  },

  // Brand actions
  brand_actions__brand_create: {
    render: ({ onSubmit, onClose, isSubmitting, isOpen, actionLabel }) => {
      return (
        <CreateBrandForm
          isOpen={isOpen}
          onClose={onClose}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },
  brand_actions__brand_update: {
    render: ({
      objectData,
      onSubmit,
      onClose,
      isSubmitting,
      isOpen,
      actionLabel,
    }) => {
      // objectData is typed as BrandSchema | undefined
      return (
        <UpdateBrandForm
          isOpen={isOpen}
          onClose={onClose}
          defaultValues={objectData}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },
  brand_actions__brand_delete: {
    render: () => null,
  },

  // Campaign actions (additional)

  // Invoice actions
  invoice_actions__invoice_create: {
    render: () => null, // TODO: Implement CreateInvoiceForm
  },
  invoice_actions__invoice_update: {
    render: () => null, // TODO: Implement UpdateInvoiceForm
  },
  invoice_actions__invoice_delete: {
    render: () => null,
  },

  // Media actions (additional)
  media_actions__media_update: {
    render: () => null, // TODO: Implement UpdateMediaForm
  },
  media_actions__media_delete: {
    render: () => null,
  },
  media_actions__media_download: {
    render: () => null,
  },

  // Deliverable media actions
  deliverable_media_actions__deliverable_media_accept: {
    render: () => null,
  },
  deliverable_media_actions__deliverable_media_reject: {
    render: () => null,
  },
  deliverable_media_actions__deliverable_media_remove_media: {
    render: () => null,
  },

  // Dashboard actions
  dashboard_actions__create: {
    render: ({ onSubmit, onClose, isSubmitting, isOpen, actionLabel }) => {
      return (
        <CreateDashboardForm
          isOpen={isOpen}
          onClose={onClose}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },
  dashboard_actions__edit: {
    // Edit mode toggle - no form needed, handled by editMode prop in ObjectActions
    render: () => null,
  },
  dashboard_actions__delete: {
    render: () => null,
  },
  dashboard_actions__update: {
    render: ({
      objectData,
      onSubmit,
      onClose,
      isSubmitting,
      isOpen,
      actionLabel,
    }) => {
      return (
        <UpdateDashboardForm
          isOpen={isOpen}
          onClose={onClose}
          defaultValues={objectData}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },

  // Widget actions
  widget_actions__create: {
    render: () => null, // Widget creation is handled in dashboard-content.tsx
  },
  widget_actions__edit: {
    render: ({
      objectData,
      onSubmit,
      onClose,
      isSubmitting,
      isOpen,
      actionLabel,
    }) => {
      return (
        <UpdateWidgetForm
          isOpen={isOpen}
          onOpenChange={(open) => {
            if (!open) onClose();
          }}
          widget={objectData as WidgetSchema}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },
  widget_actions__delete: {
    render: () => null,
  },

  // Team actions
  team_actions__team_delete: {
    render: () => null,
  },
  team_actions__team_invite_user: {
    render: ({ onSubmit, onClose, isSubmitting, isOpen, actionLabel }) => {
      return (
        <InviteUserToTeamForm
          isOpen={isOpen}
          onClose={onClose}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
          actionLabel={actionLabel}
        />
      );
    },
  },

  // Message actions
  message_actions__delete: {
    render: () => null,
  },
  message_actions__update: {
    render: () => null,
  },

  // Document actions
  document_actions__document_update: {
    render: () => null,
  },
  document_actions__document_delete: {
    render: () => null,
  },
  document_actions__document_download: {
    render: () => null,
  },
  document_actions__document_register: {
    render: () => null,
  },

  // Campaign contract actions
  campaign_actions__campaign_add_contract: {
    render: () => null,
  },
  campaign_actions__campaign_replace_contract: {
    render: () => null,
  },
};

/**
 * Get the render function for a given action type
 * Returns the render function with proper typing based on the action
 */
export function getActionRenderer(
  actionType: ActionType
): ActionRegistryEntry<unknown, DomainObject>['render'] | undefined {
  const entry = actionRegistry[actionType];
  // Type assertion needed because we're losing the specific types from ActionRegistry
  return entry?.render as
    | ActionRegistryEntry<unknown, DomainObject>['render']
    | undefined;
}
