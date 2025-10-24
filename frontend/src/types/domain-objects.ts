/**
 * Union type of all domain-specific response schemas
 *
 * This type represents the various object types that can be returned from
 * detail endpoints and used with the ObjectActions component.
 */

import type {
  ObjectDetailDTO,
  DeliverableResponseSchema,
  MediaResponseSchema,
  CampaignSchema,
  BrandSchema,
} from '@/openapi/managerLab.schemas';

/**
 * Domain object type - represents any object with an id and actions
 */
export type DomainObject =
  | ObjectDetailDTO
  | DeliverableResponseSchema
  | MediaResponseSchema
  | CampaignSchema
  | BrandSchema;
