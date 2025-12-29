import { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

type DataTableSearchProps = {
  value: string;
  onChangeAction: (value: string) => void;
  placeholder?: string;
  debounceMs?: number;
};

export function DataTableSearch({
  value,
  onChangeAction,
  placeholder = 'Search...',
  debounceMs = 300,
}: DataTableSearchProps) {
  const [localValue, setLocalValue] = useState(value);

  // Update local value when external value changes
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  // Debounce the onChange callback
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      const trimmed = localValue.trim();
      if (trimmed !== value) {
        onChangeAction(trimmed);
      }
    }, debounceMs);

    return () => clearTimeout(timeoutId);
  }, [localValue, debounceMs, onChangeAction, value]);

  const handleClear = () => {
    setLocalValue('');
    onChangeAction('');
  };

  return (
    <div className="relative w-full ">
      <Search className="text-muted-foreground pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2" />
      <Input
        type="search"
        value={localValue}
        onChange={(event) => setLocalValue(event.target.value)}
        placeholder={placeholder}
        className="w-full pl-9"
        aria-label={placeholder}
      />
      {localValue.length > 0 ? (
        <Button
          variant="ghost"
          size="sm"
          className="text-muted-foreground hover:text-foreground absolute right-1 top-1/2 h-7 w-7 -translate-y-1/2 p-0"
          onClick={handleClear}
        >
          <span className="sr-only">Clear search</span>
          <X className="h-3 w-3" />
        </Button>
      ) : null}
    </div>
  );
}
