import { X } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { humanizeEnumValue } from '@/lib/format';

interface EnumFilterFieldProps {
  availableValues: string[];
  selectedValues: string[];
  onChange: (values: string[]) => void;
  maxHeight?: string;
}

/**
 * Generic enum filter field component that can be used inline in forms
 * Shows checkboxes for selection and badges for selected values
 *
 * Used by:
 * - EnumFilter (data-table) with Apply button
 * - Widget configuration forms (inline, onChange)
 */
export function EnumFilterField({
  availableValues,
  selectedValues,
  onChange,
  maxHeight = 'max-h-32',
}: EnumFilterFieldProps) {
  const toggleValue = (value: string) => {
    const isSelected = selectedValues.includes(value);

    if (isSelected) {
      onChange(selectedValues.filter((v) => v !== value));
    } else {
      onChange([...selectedValues, value]);
    }
  };

  const removeValue = (value: string) => {
    onChange(selectedValues.filter((v) => v !== value));
  };

  return (
    <div className="space-y-2">
      {/* Selected values display */}
      {selectedValues.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedValues.map((value) => (
            <Badge key={value} variant="secondary" className="gap-1">
              {humanizeEnumValue(value)}
              <Button
                type="button"
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
      <div className={`${maxHeight} space-y-2 overflow-y-auto`}>
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
    </div>
  );
}
