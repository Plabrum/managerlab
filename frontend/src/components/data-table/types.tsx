import type {
  ColumnDefinitionSchema,
  ObjectListRequestFiltersItem,
} from '@/openapi/ariveAPI.schemas';

// Re-export the API types for backward compatibility
export type DataTableColumn = ColumnDefinitionSchema;
export type DataTableFilter = ObjectListRequestFiltersItem;
