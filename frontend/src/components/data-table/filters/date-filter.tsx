import * as React from 'react';
import { format } from 'date-fns';
import { CalendarIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';
import type { DateFilterDefinition } from '@/openapi/ariveAPI.schemas';

interface DatePickerProps {
  date?: Date;
  onDateChange: (date: Date | undefined) => void;
  placeholder: string;
}

function DatePicker({ date, onDateChange, placeholder }: DatePickerProps) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            'w-full justify-start text-left font-normal',
            !date && 'text-muted-foreground'
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {date ? format(date, 'PPP') : placeholder}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0">
        <Calendar
          mode="single"
          selected={date}
          onSelect={onDateChange}
          initialFocus
        />
      </PopoverContent>
    </Popover>
  );
}

interface DateFilterProps {
  column: string;
  initialFilter?: DateFilterDefinition;
  onSubmit: (filter: DateFilterDefinition) => void;
  onClear?: () => void;
}

export function DateFilter({
  column,
  initialFilter,
  onSubmit,
  onClear,
}: DateFilterProps) {
  const [startDate, setStartDate] = React.useState<Date | undefined>(
    initialFilter?.start ? new Date(initialFilter.start) : undefined
  );
  const [endDate, setEndDate] = React.useState<Date | undefined>(
    initialFilter?.finish ? new Date(initialFilter.finish) : undefined
  );

  const handleSubmit = () => {
    if (!startDate && !endDate) return;

    onSubmit({
      column,
      start: startDate?.toISOString() || null,
      finish: endDate?.toISOString() || null,
      type: 'date_filter',
    });
  };

  const handleClear = () => {
    if (onClear) {
      onClear();
    } else {
      setStartDate(undefined);
      setEndDate(undefined);
    }
  };

  const hasValue = startDate || endDate;

  return (
    <div className="space-y-2">
      <DatePicker
        date={startDate}
        onDateChange={setStartDate}
        placeholder="Start date"
      />
      <DatePicker
        date={endDate}
        onDateChange={setEndDate}
        placeholder="End date"
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
