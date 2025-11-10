'use client';

import * as React from 'react';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { EnumFilterDefinition } from '@/openapi/ariveAPI.schemas';
import { humanizeEnumValue } from '@/lib/format';

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

  const toggleValue = (value: string) => {
    const isSelected = selectedValues.includes(value);

    if (isSelected) {
      setSelectedValues(selectedValues.filter((v) => v !== value));
    } else {
      setSelectedValues([...selectedValues, value]);
    }
  };

  const removeValue = (value: string) => {
    setSelectedValues(selectedValues.filter((v) => v !== value));
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
      {/* Selected values display */}
      {selectedValues.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedValues.map((value) => (
            <Badge key={value} variant="secondary" className="gap-1">
              {humanizeEnumValue(value)}
              <Button
                variant="ghost"
                size="sm"
                className="h-auto p-0 hover:bg-transparent"
                onClick={() => removeValue(value)}
              >
                <X className="h-3 w-3" />
              </Button>
            </Badge>
          ))}
        </div>
      )}

      {/* Available options */}
      <div className="max-h-32 space-y-2 overflow-y-auto">
        {availableValues.map((value) => (
          <div key={value} className="flex items-center space-x-2">
            <Checkbox
              id={`enum-${value}`}
              checked={selectedValues.includes(value)}
              onCheckedChange={() => toggleValue(value)}
            />
            <label
              htmlFor={`enum-${value}`}
              className="cursor-pointer text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              {humanizeEnumValue(value)}
            </label>
          </div>
        ))}
      </div>

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
