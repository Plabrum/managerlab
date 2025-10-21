import type { ComponentType } from 'react';
import type {
  ActionsActionGroupExecuteActionBody,
  ActionsActionGroupObjectIdExecuteObjectActionBody,
  ObjectDetailDTO,
} from '@/openapi/managerLab.schemas';
import { UpdateDeliverableActionForm } from './forms/update-deliverable-action-form';
import { CreateDeliverableActionForm } from './forms/create-deliverable-action-form';

/**
 * Props that all action form components must accept
 */
export interface ActionFormProps<TData = unknown> {
  defaultValues?: Partial<TData>;
  onSubmit: (data: TData) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Registry entry for an action
 */
export interface ActionRegistryEntry<TData = unknown> {
  /**
   * The form component to render for this action
   * If null, the action will be executed directly without a form
   */
  FormComponent: ComponentType<ActionFormProps<TData>> | null;

  /**
   * Pure function to extract default values from object data
   * This is automatically called when objectData is provided to ObjectActions/ActionsMenu
   * Only needed for actions that require pre-filled forms (e.g., update actions)
   */
  extractDefaultValues?: (
    objectData: ObjectDetailDTO
  ) => Partial<TData> | undefined;
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
 * The central action registry
 * This is where all action forms are registered
 *
 * Actions with FormComponent = null will be executed directly without showing a form
 * Actions not in the registry will also be executed directly
 */
export const actionRegistry: ActionRegistry = {
  // Deliverable actions
  deliverable_actions__deliverable_update: {
    FormComponent: UpdateDeliverableActionForm,
    extractDefaultValues: (objectData) => {
      // Extract fields from objectData to pre-fill the update form
      const getFieldValue = (key: string) => {
        const field = objectData.fields.find((f) => f.key === key);
        return field?.value;
      };

      return {
        title: objectData.title,
        content: getFieldValue('content') as string | null | undefined,
        platforms: getFieldValue('platforms') as unknown,
        posting_date: getFieldValue('posting_date') as string | undefined,
        notes: getFieldValue('notes') as unknown,
        compensation_structure: getFieldValue(
          'compensation_structure'
        ) as unknown,
        campaign_id: getFieldValue('campaign_id') as number | undefined,
      };
    },
  },
  top_level_deliverable_actions__top_level_deliverable_create: {
    FormComponent: CreateDeliverableActionForm,
    // No extractDefaultValues - create forms start empty
  },

  // Actions without forms (executed directly)
  deliverable_actions__deliverable_delete: {
    FormComponent: null,
  },
  deliverable_actions__deliverable_publish: {
    FormComponent: null,
  },
  deliverable_actions__deliverable_add_media: {
    FormComponent: null, // TODO: Add form if needed
  },
  deliverable_actions__deliverable_remove_media: {
    FormComponent: null, // TODO: Add form if needed
  },

  // Other action groups can be added here as needed
};

/**
 * Get the form component for a given action type
 * Returns ComponentType with unknown data type for flexibility
 */
export function getActionFormComponent(
  actionType: ActionType
): ComponentType<ActionFormProps<unknown>> | null | undefined {
  const entry = actionRegistry[actionType];
  return entry?.FormComponent as
    | ComponentType<ActionFormProps<unknown>>
    | null
    | undefined;
}

/**
 * Get the default values extractor for a given action type
 */
export function getActionDefaultValuesExtractor(
  actionType: ActionType
):
  | ((objectData: ObjectDetailDTO) => Record<string, unknown> | undefined)
  | undefined {
  const entry = actionRegistry[actionType];
  return entry?.extractDefaultValues as
    | ((objectData: ObjectDetailDTO) => Record<string, unknown> | undefined)
    | undefined;
}

/**
 * Check if an action has a form component registered
 */
export function hasActionForm(actionType: ActionType): boolean {
  const component = getActionFormComponent(actionType);
  return component !== null && component !== undefined;
}
