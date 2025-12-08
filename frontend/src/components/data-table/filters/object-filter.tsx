'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';
import type {
  ObjectFilterDefinition,
  ObjectTypes,
} from '@/openapi/ariveAPI.schemas';
import { ObjectFilterField } from '@/components/forms/filters';

interface ObjectFilterProps {
  column: string;
  objectType: ObjectTypes;
  initialFilter?: ObjectFilterDefinition;
  onSubmit: (filter: ObjectFilterDefinition) => void;
  onClear?: () => void;
}

export function ObjectFilter({
  column,
  objectType,
  initialFilter,
  onSubmit,
  onClear,
}: ObjectFilterProps) {
  const [selectedIds, setSelectedIds] = React.useState<string[]>(
    initialFilter?.values || []
  );

  const handleSubmit = () => {
    if (selectedIds.length === 0) return;

    onSubmit({
      column,
      values: selectedIds,
      type: 'object_filter',
    });
  };

  const handleClear = () => {
    if (onClear) {
      onClear();
    } else {
      setSelectedIds([]);
    }
  };

  return (
    <div className="space-y-3">
      <ObjectFilterField
        objectType={objectType}
        selectedIds={selectedIds}
        onChange={setSelectedIds}
        placeholder={`Select ${objectType}...`}
      />

      <div className="flex gap-2 pt-2">
        <Button
          onClick={handleSubmit}
          className="flex-1"
          disabled={selectedIds.length === 0}
        >
          Apply Filter
        </Button>
        <Button variant="outline" onClick={handleClear}>
          Clear
        </Button>
      </div>
    </div>
  );
}
