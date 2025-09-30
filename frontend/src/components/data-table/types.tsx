import type {
  ColumnDefinitionDTO,
  ObjectListRequestFiltersItem,
} from '@/openapi/managerLab.schemas';

// Re-export the API types for backward compatibility
export type DataTableColumn = ColumnDefinitionDTO;
export type DataTableFilter = ObjectListRequestFiltersItem;
