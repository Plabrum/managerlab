'use client';

import * as React from 'react';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import type {
  TextFilterDefinition,
  TextFilterDefinitionOperation,
} from '@/openapi/ariveAPI.schemas';

interface TextFilterProps {
  column: string;
  initialFilter?: TextFilterDefinition;
  onSubmit: (filter: TextFilterDefinition) => void;
  onClear?: () => void;
}

export function TextFilter({
  column,
  initialFilter,
  onSubmit,
  onClear,
}: TextFilterProps) {
  const [operation, setOperation] =
    React.useState<TextFilterDefinitionOperation>(
      initialFilter?.operation || 'contains'
    );
  const [value, setValue] = React.useState(initialFilter?.value || '');

  const handleSubmit = () => {
    if (!value.trim()) return;

    onSubmit({
      column,
      operation,
      value: value.trim(),
      type: 'text_filter',
    });
  };

  const handleClear = () => {
    if (onClear) {
      onClear();
    } else {
      setOperation('contains');
      setValue('');
    }
  };

  return (
    <div className="space-y-2">
      <Select
        value={operation}
        onValueChange={(value) =>
          setOperation(value as TextFilterDefinitionOperation)
        }
      >
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="contains">Contains</SelectItem>
          <SelectItem value="starts_with">Starts with</SelectItem>
          <SelectItem value="ends_with">Ends with</SelectItem>
          <SelectItem value="equals">Equals</SelectItem>
        </SelectContent>
      </Select>
      <Input
        placeholder="Enter value..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            handleSubmit();
          }
        }}
      />
      <div className="flex gap-2 pt-2">
        <Button
          onClick={handleSubmit}
          className="flex-1"
          disabled={!value.trim()}
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
