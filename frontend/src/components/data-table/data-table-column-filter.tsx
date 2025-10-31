'use client';

import * as React from 'react';
import type {
  ColumnDefinitionSchema,
  ObjectListRequestFiltersItem,
} from '@/openapi/managerLab.schemas';
import {
  TextFilter,
  RangeFilter,
  DateFilter,
  BooleanFilter,
  EnumFilter,
  ObjectFilter,
} from './filters';

interface DataTableColumnFilterProps {
  column: ColumnDefinitionSchema;
  filters: ObjectListRequestFiltersItem[];
  onFiltersChange: (filters: ObjectListRequestFiltersItem[]) => void;
}

export function DataTableColumnFilter({
  column: column,
  filters,
  onFiltersChange,
}: DataTableColumnFilterProps) {
  const handleSubmit = (newFilter: ObjectListRequestFiltersItem) => {
    onFiltersChange([...filters, newFilter]);
  };

  switch (column.filter_type) {
    case 'text_filter':
      return (
        <DataTableColumnFilterWrapper label={column.label}>
          <TextFilter column={column.key} onSubmit={handleSubmit} />
        </DataTableColumnFilterWrapper>
      );
    case 'range_filter':
      return (
        <DataTableColumnFilterWrapper label={column.label}>
          <RangeFilter column={column.key} onSubmit={handleSubmit} />
        </DataTableColumnFilterWrapper>
      );
    case 'date_filter':
      return (
        <DataTableColumnFilterWrapper label={column.label}>
          <DateFilter column={column.key} onSubmit={handleSubmit} />
        </DataTableColumnFilterWrapper>
      );
    case 'boolean_filter':
      return (
        <DataTableColumnFilterWrapper label={column.label}>
          <BooleanFilter column={column.key} onSubmit={handleSubmit} />
        </DataTableColumnFilterWrapper>
      );
    case 'enum_filter':
      return (
        <DataTableColumnFilterWrapper label={column.label}>
          <EnumFilter
            column={column.key}
            onSubmit={handleSubmit}
            availableValues={column.available_values || []}
          />
        </DataTableColumnFilterWrapper>
      );
    case 'object_filter':
      if (!column.object_type) {
        console.error('object_filter requires object_type to be set');
        return null;
      }
      return (
        <DataTableColumnFilterWrapper label={column.label}>
          <ObjectFilter
            column={column.key}
            objectType={column.object_type}
            onSubmit={handleSubmit}
          />
        </DataTableColumnFilterWrapper>
      );
  }
}

function DataTableColumnFilterWrapper({
  label,
  children,
}: {
  label?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="w-80 space-y-4 p-4">
      <div className="space-y-2">
        <h4 className="text-sm font-medium">Filter {label}</h4>
      </div>

      <div className="space-y-3">{children}</div>
    </div>
  );
}
