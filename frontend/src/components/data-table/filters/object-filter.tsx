'use client';

import * as React from 'react';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type {
  ObjectFilterDefinition,
  ObjectTypes,
} from '@/openapi/managerLab.schemas';
import { ObjectSearchCombobox } from '@/components/forms/object-search-combobox';

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
  const [currentSelection, setCurrentSelection] = React.useState<string | null>(
    null
  );

  const handleSubmit = () => {
    if (selectedIds.length === 0) return;

    onSubmit({
      column,
      values: selectedIds,
      type: 'object_filter',
    });
  };

  const handleAddSelection = (id: string | null) => {
    if (id && !selectedIds.includes(id)) {
      setSelectedIds([...selectedIds, id]);
    }
    setCurrentSelection(null);
  };

  const removeId = (id: string) => {
    setSelectedIds(selectedIds.filter((v) => v !== id));
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
      {/* Object search combobox */}
      <ObjectSearchCombobox
        objectType={objectType}
        value={currentSelection}
        onValueChange={handleAddSelection}
        placeholder={`Select ${objectType}...`}
        allowCreate={false}
      />

      {/* Selected objects display */}
      {selectedIds.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedIds.map((id) => (
            <Badge key={id} variant="secondary" className="gap-1">
              {id}
              <Button
                variant="ghost"
                size="sm"
                className="h-auto p-0 hover:bg-transparent"
                onClick={() => removeId(id)}
              >
                <X className="h-3 w-3" />
              </Button>
            </Badge>
          ))}
        </div>
      )}

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
