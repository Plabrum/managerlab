'use client';

import * as React from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import type { RangeFilterDefinition } from '@/openapi/ariveAPI.schemas';

interface RangeFilterProps {
  column: string;
  initialFilter?: RangeFilterDefinition;
  onSubmit: (filter: RangeFilterDefinition) => void;
  onClear?: () => void;
}

export function RangeFilter({
  column,
  initialFilter,
  onSubmit,
  onClear,
}: RangeFilterProps) {
  const [start, setStart] = React.useState<number | null>(
    initialFilter?.start || null
  );
  const [finish, setFinish] = React.useState<number | null>(
    initialFilter?.finish || null
  );

  const handleSubmit = () => {
    if (start === null && finish === null) return;

    onSubmit({
      column,
      start,
      finish,
      type: 'range_filter',
    });
  };

  const handleClear = () => {
    if (onClear) {
      onClear();
    } else {
      setStart(null);
      setFinish(null);
    }
  };

  const hasValue = start !== null || finish !== null;

  return (
    <div className="flex items-center gap-2">
      <Input
        type="number"
        placeholder="Min"
        value={start ?? ''}
        onChange={(e) =>
          setStart(e.target.value ? Number(e.target.value) : null)
        }
      />
      <span className="text-muted-foreground text-sm">to</span>
      <Input
        type="number"
        placeholder="Max"
        value={finish ?? ''}
        onChange={(e) =>
          setFinish(e.target.value ? Number(e.target.value) : null)
        }
      />
      <div className="flex gap-2 pt-2">
        <Button onClick={handleSubmit} className="flex-1" disabled={!hasValue}>
          Apply Filter
        </Button>
        <Button variant="outline" onClick={handleClear}>
          Clear
        </Button>
      </div>
    </div>
  );
}
