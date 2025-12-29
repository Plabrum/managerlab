import * as React from 'react';
import { EnumFilterField } from '@/components/forms/filters';
import { Button } from '@/components/ui/button';
import type { EnumFilterDefinition } from '@/openapi/ariveAPI.schemas';

interface EnumFilterProps {
  column: string;
  initialFilter?: EnumFilterDefinition;
  onSubmit: (filter: EnumFilterDefinition) => void;
  onClear?: () => void;
  availableValues: string[];
}

export function EnumFilter({
  column,
  initialFilter,
  onSubmit,
  onClear,
  availableValues,
}: EnumFilterProps) {
  const [selectedValues, setSelectedValues] = React.useState<string[]>(
    initialFilter?.values || []
  );

  const handleSubmit = () => {
    if (selectedValues.length === 0) return;

    onSubmit({
      column,
      values: selectedValues,
      type: 'enum_filter',
    });
  };

  const handleClear = () => {
    if (onClear) {
      onClear();
    } else {
      setSelectedValues([]);
    }
  };

  return (
    <div className="space-y-3">
      <EnumFilterField
        availableValues={availableValues}
        selectedValues={selectedValues}
        onChange={setSelectedValues}
      />

      <div className="flex gap-2 pt-2">
        <Button
          onClick={handleSubmit}
          className="flex-1"
          disabled={selectedValues.length === 0}
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
