'use client';

import * as React from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import type { BooleanFilterDefinition } from '@/openapi/managerLab.schemas';

interface BooleanFilterProps {
  column: string;
  initialFilter?: BooleanFilterDefinition;
  onSubmit: (filter: BooleanFilterDefinition) => void;
  onClear?: () => void;
}

export function BooleanFilter({
  column,
  initialFilter,
  onSubmit,
  onClear,
}: BooleanFilterProps) {
  const [value, setValue] = React.useState<boolean | undefined>(
    initialFilter?.value
  );

  const handleSubmit = () => {
    if (value === undefined) return;

    onSubmit({
      column,
      value,
      type: 'boolean_filter',
    });
  };

  const handleClear = () => {
    if (onClear) {
      onClear();
    } else {
      setValue(undefined);
    }
  };

  return (
    <div className="space-y-3">
      <Select
        value={value !== undefined ? String(value) : ''}
        onValueChange={(val) => setValue(val === 'true')}
      >
        <SelectTrigger>
          <SelectValue placeholder="Select value..." />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="true">Yes</SelectItem>
          <SelectItem value="false">No</SelectItem>
        </SelectContent>
      </Select>
      <div className="flex gap-2 pt-2">
        <Button
          onClick={handleSubmit}
          className="flex-1"
          disabled={value === undefined}
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
