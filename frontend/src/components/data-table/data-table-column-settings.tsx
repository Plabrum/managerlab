'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Settings } from 'lucide-react';
import type { DataTableColumn } from './types';

interface DataTableColumnSettingsProps {
  columns: DataTableColumn[];
  visibleColumns: string[];
  onVisibleColumnsChange: (visibleColumns: string[]) => void;
}

export function DataTableColumnSettings({
  columns,
  visibleColumns,
  onVisibleColumnsChange,
}: DataTableColumnSettingsProps) {
  const [isOpen, setIsOpen] = React.useState(false);

  const handleColumnToggle = (columnKey: string, checked: boolean) => {
    if (checked) {
      onVisibleColumnsChange([...visibleColumns, columnKey]);
    } else {
      onVisibleColumnsChange(visibleColumns.filter((key) => key !== columnKey));
    }
  };

  const handleSelectAll = () => {
    onVisibleColumnsChange(columns.map((col) => col.key));
  };

  const handleDeselectAll = () => {
    onVisibleColumnsChange([]);
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" size="icon">
          <Settings className="h-4 w-4" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-64" align="end">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium">Column Settings</h4>
            <div className="flex gap-1">
              <Button variant="ghost" size="sm" onClick={handleSelectAll}>
                All
              </Button>
              <Button variant="ghost" size="sm" onClick={handleDeselectAll}>
                None
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            {columns.map((column) => (
              <div key={column.key} className="flex items-center space-x-2">
                <Checkbox
                  id={column.key}
                  checked={visibleColumns.includes(column.key)}
                  onCheckedChange={(checked) =>
                    handleColumnToggle(column.key, !!checked)
                  }
                />
                <label
                  htmlFor={column.key}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {column.label}
                </label>
              </div>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
