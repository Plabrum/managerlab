'use client';

import * as React from 'react';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { ObjectTypes } from '@/openapi/ariveAPI.schemas';
import { ObjectSearchCombobox } from '@/components/forms/object-search-combobox';

interface ObjectFilterFieldProps {
  objectType: ObjectTypes;
  selectedIds: string[];
  onChange: (ids: string[]) => void;
  placeholder?: string;
}

/**
 * Generic object filter field component that can be used inline in forms
 * Shows a searchable combobox and badges for selected objects
 *
 * Used by:
 * - ObjectFilter (data-table) with Apply button
 * - Widget configuration forms (inline, onChange)
 */
export function ObjectFilterField({
  objectType,
  selectedIds,
  onChange,
  placeholder,
}: ObjectFilterFieldProps) {
  const [currentSelection, setCurrentSelection] = React.useState<string | null>(
    null
  );

  const handleAddSelection = (id: string | null) => {
    if (id && !selectedIds.includes(id)) {
      onChange([...selectedIds, id]);
    }
    setCurrentSelection(null);
  };

  const removeId = (id: string) => {
    onChange(selectedIds.filter((v) => v !== id));
  };

  return (
    <div className="space-y-2">
      {/* Object search combobox */}
      <ObjectSearchCombobox
        objectType={objectType}
        value={currentSelection}
        onValueChange={handleAddSelection}
        placeholder={placeholder || `Select ${objectType}...`}
        allowCreate={false}
      />

      {/* Selected objects display */}
      {selectedIds.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedIds.map((id) => (
            <Badge key={id} variant="secondary" className="gap-1">
              {id}
              <Button
                type="button"
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
    </div>
  );
}
