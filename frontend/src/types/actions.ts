import type { ActionDTO, ActionGroupType } from '@/openapi/managerLab.schemas';
import type { DomainObject } from './domain-objects';

/**
 * Object-level actions - actions performed on a specific object instance
 */
export interface ObjectActionData {
  data: DomainObject;
  actionGroup: ActionGroupType;
  onRefetch?: () => void;
  onActionComplete?: (action: ActionDTO, response: unknown) => void;
}

/**
 * Top-level actions - actions not tied to a specific object (e.g., "Create Brand")
 */
export interface TopLevelActionData {
  actions?: ActionDTO[];
  actionGroup: ActionGroupType;
  onInvalidate?: () => void;
  onActionComplete?: (action: ActionDTO, response: unknown) => void;
}
