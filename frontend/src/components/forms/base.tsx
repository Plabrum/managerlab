import * as React from 'react';
import { format } from 'date-fns';
import { CalendarIcon, Check, ChevronsUpDown, X } from 'lucide-react';
import {
  useForm,
  FormProvider,
  useFormContext,
  type FieldValues,
  type Path,
  type RegisterOptions,
  type SubmitHandler,
  type UseFormProps,
  type DefaultValues,
  Controller,
} from 'react-hook-form';
import { Calendar } from '@/components/ui/calendar';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from '@/components/ui/drawer';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Textarea } from '@/components/ui/textarea';
import { useIsMobile } from '@/hooks/use-mobile';
import { cn } from '@/lib/utils'; // optional: your className helper
import { ImageUploadField } from './image-upload-dropzone';
import { COUNTRY_OPTIONS, US_STATE_OPTIONS } from './utils';
import { Button } from '../ui/button';

type BaseFieldProps<
  TFieldValues extends FieldValues,
  N extends Path<TFieldValues>,
> = {
  name: N;
  label?: string;
  placeholder?: string;
  required?: boolean | string; // true|"Custom required message"
  className?: string;
  rules?: RegisterOptions<TFieldValues, N>;
  description?: string;
  // For aria & layout control
  id?: string;
};

// eslint-disable-next-line react-refresh/only-export-components
function RequiredMessage(required?: boolean | string) {
  if (!required) return undefined;
  return typeof required === 'string' ? required : 'This field is required';
}

// eslint-disable-next-line react-refresh/only-export-components
function FieldError({ name }: { name: string }) {
  const {
    formState: { errors },
  } = useFormContext();
  const err = errors?.[name] as { message?: string } | undefined;
  if (!err) return null;
  return (
    <p className="text-destructive mt-1 text-sm">
      {String(err.message ?? 'Invalid value')}
    </p>
  );
}

export function createTypedForm<TFieldValues extends FieldValues>() {
  type Name<N extends Path<TFieldValues>> = N;

  // ---------- Form wrapper ----------
  function Form(props: {
    defaultValues?: DefaultValues<TFieldValues>;
    onSubmit: SubmitHandler<TFieldValues>;
    className?: string;
    children: React.ReactNode;
    mode?: UseFormProps<TFieldValues>['mode'];
    reValidateMode?: UseFormProps<TFieldValues>['reValidateMode'];
    resolver?: UseFormProps<TFieldValues>['resolver'];
  }) {
    const {
      defaultValues,
      onSubmit,
      className,
      children,
      mode = 'onSubmit',
      reValidateMode = 'onChange',
      resolver,
    } = props;
    const methods = useForm<TFieldValues>({
      defaultValues,
      mode,
      reValidateMode,
      resolver,
    });

    // Clean up empty address objects before submission
    const handleSubmit = React.useCallback(
      (data: TFieldValues) => {
        const cleanData = { ...data } as Record<string, unknown>;

        // Check if address field exists and clean it up if all subfields are empty
        if ('address' in cleanData && cleanData.address !== null) {
          const address = cleanData.address as Record<string, unknown>;
          const isEmpty = (val: unknown) =>
            val === null ||
            val === undefined ||
            (typeof val === 'string' && val.trim() === '');

          const allFieldsEmpty =
            isEmpty(address.address1) &&
            isEmpty(address.address2) &&
            isEmpty(address.city) &&
            isEmpty(address.state) &&
            isEmpty(address.zip) &&
            isEmpty(address.country);

          if (allFieldsEmpty) {
            cleanData.address = null;
          }
        }

        onSubmit(cleanData as TFieldValues);
      },
      [onSubmit]
    );

    return (
      <FormProvider {...methods}>
        <form
          onSubmit={methods.handleSubmit(handleSubmit)}
          className={cn('space-y-4', className)}
        >
          {children}
          {/* keep native submit available for Enter key / programmatic submit */}
          <button type="submit" className="hidden" />
        </form>
      </FormProvider>
    );
  }

  // ---------- String input ----------
  function FormString<N extends Name<Path<TFieldValues>>>(
    props: BaseFieldProps<TFieldValues, N> & {
      type?: React.ComponentProps<'input'>['type'];
      autoFocus?: boolean;
    }
  ) {
    const {
      name,
      label,
      placeholder,
      required,
      className,
      rules,
      description,
      id,
      autoFocus,
      type,
    } = props;
    const { register } = useFormContext<TFieldValues>();
    const htmlId = id ?? String(name);

    return (
      <div className={className}>
        {label && (
          <Label htmlFor={htmlId}>
            {label} {required ? '*' : null}
          </Label>
        )}
        <Input
          id={htmlId}
          type={type ?? 'text'}
          autoFocus={autoFocus}
          {...register(name, {
            required: RequiredMessage(required),
            ...rules,
          })}
          className="mt-1"
          placeholder={placeholder}
        />
        {description ? (
          <p className="text-muted-foreground mt-1 text-xs">{description}</p>
        ) : null}
        <FieldError name={String(name)} />
      </div>
    );
  }

  // ---------- Email input with sane default pattern ----------
  function FormEmail<N extends Name<Path<TFieldValues>>>(
    props: BaseFieldProps<TFieldValues, N>
  ) {
    const {
      name,
      label,
      placeholder,
      required,
      className,
      rules,
      description,
      id,
    } = props;
    const { register } = useFormContext<TFieldValues>();
    const htmlId = id ?? String(name);

    // RFC5322-lite, case-insensitive
    const defaultEmailPattern = {
      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
      message: 'Invalid email address',
    };

    return (
      <div className={className}>
        {label && (
          <Label htmlFor={htmlId}>
            {label} {required ? '*' : null}
          </Label>
        )}
        <Input
          id={htmlId}
          type="email"
          {...register(name, {
            required: RequiredMessage(required),
            pattern: rules?.pattern || defaultEmailPattern,
            ...rules,
          } as RegisterOptions<TFieldValues, N>)}
          className="mt-1"
          placeholder={placeholder}
        />
        {description ? (
          <p className="text-muted-foreground mt-1 text-xs">{description}</p>
        ) : null}
        <FieldError name={String(name)} />
      </div>
    );
  }

  // ---------- Number input ----------
  function FormNumber<N extends Name<Path<TFieldValues>>>(
    props: BaseFieldProps<TFieldValues, N> & {
      min?: number;
      max?: number;
      step?: number;
      /** If true, uses type="tel" for better mobile experience (no spinners) */
      useTelInput?: boolean;
    }
  ) {
    const {
      name,
      label,
      placeholder,
      required,
      className,
      rules,
      description,
      id,
      min,
      max,
      step,
      useTelInput = false,
    } = props;
    const { register } = useFormContext<TFieldValues>();
    const htmlId = id ?? String(name);

    return (
      <div className={className}>
        {label && (
          <Label htmlFor={htmlId}>
            {label} {required ? '*' : null}
          </Label>
        )}
        <Input
          id={htmlId}
          type={useTelInput ? 'tel' : 'number'}
          min={min}
          max={max}
          step={step}
          {...register(name, {
            required: RequiredMessage(required),
            min:
              min !== undefined
                ? { value: min, message: `Minimum value is ${min}` }
                : undefined,
            max:
              max !== undefined
                ? { value: max, message: `Maximum value is ${max}` }
                : undefined,
            ...(useTelInput ? {} : { valueAsNumber: true }),
            ...rules,
          } as RegisterOptions<TFieldValues, N>)}
          className="mt-1"
          placeholder={placeholder}
        />
        {description ? (
          <p className="text-muted-foreground mt-1 text-xs">{description}</p>
        ) : null}
        <FieldError name={String(name)} />
      </div>
    );
  }

  // ---------- Multiline text ----------
  function FormText<N extends Name<Path<TFieldValues>>>(
    props: BaseFieldProps<TFieldValues, N> & { rows?: number; resize?: boolean }
  ) {
    const {
      name,
      label,
      placeholder,
      required,
      className,
      rules,
      rows = 3,
      description,
      id,
      resize = false,
    } = props;
    const { register } = useFormContext<TFieldValues>();
    const htmlId = id ?? String(name);

    return (
      <div className={className}>
        {label && (
          <Label htmlFor={htmlId}>
            {label} {required ? '*' : null}
          </Label>
        )}
        <Textarea
          id={htmlId}
          {...register(name, {
            required: RequiredMessage(required),
            ...rules,
          })}
          className={cn('mt-1', !resize && 'resize-none')}
          placeholder={placeholder}
          rows={rows}
        />
        {description ? (
          <p className="text-muted-foreground mt-1 text-xs">{description}</p>
        ) : null}
        <FieldError name={String(name)} />
      </div>
    );
  }

  // ---------- Select input ----------
  function FormSelect<N extends Name<Path<TFieldValues>>>(
    props: BaseFieldProps<TFieldValues, N> & {
      options: Array<{ value: string; label: string }>;
      placeholder?: string;
    }
  ) {
    const {
      name,
      label,
      placeholder,
      required,
      className,
      description,
      id,
      options,
    } = props;
    const { control } = useFormContext<TFieldValues>();
    const htmlId = id ?? String(name);

    return (
      <div className={className}>
        {label && (
          <Label htmlFor={htmlId}>
            {label} {required ? '*' : null}
          </Label>
        )}
        <Controller
          name={name}
          control={control}
          rules={{ required: RequiredMessage(required) }}
          render={({ field }) => (
            <Select
              value={field.value as string | undefined}
              onValueChange={field.onChange}
            >
              <SelectTrigger id={htmlId} className="mt-1">
                <SelectValue placeholder={placeholder} />
              </SelectTrigger>
              <SelectContent>
                {options.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        />
        {description ? (
          <p className="text-muted-foreground mt-1 text-xs">{description}</p>
        ) : null}
        <FieldError name={String(name)} />
      </div>
    );
  }

  // ---------- Combobox input (searchable select) ----------
  function FormCombobox<N extends Name<Path<TFieldValues>>>(
    props: BaseFieldProps<TFieldValues, N> & {
      options: Array<{ value: string; label: string }>;
      placeholder?: string;
      searchPlaceholder?: string;
      emptyText?: string;
    }
  ) {
    const {
      name,
      label,
      placeholder = 'Select option...',
      searchPlaceholder = 'Search...',
      emptyText = 'No results found.',
      required,
      className,
      description,
      id,
      options,
    } = props;
    const { control } = useFormContext<TFieldValues>();
    const htmlId = id ?? String(name);
    const [open, setOpen] = React.useState(false);

    return (
      <div className={className}>
        {label && (
          <Label htmlFor={htmlId}>
            {label} {required ? '*' : null}
          </Label>
        )}
        <Controller
          name={name}
          control={control}
          rules={{ required: RequiredMessage(required) }}
          render={({ field }) => (
            <div className="relative mt-1">
              <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                  <Button
                    id={htmlId}
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    className="w-full justify-between font-normal"
                  >
                    {field.value
                      ? options.find((option) => option.value === field.value)
                          ?.label
                      : placeholder}
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0" align="start">
                  <Command>
                    <CommandInput placeholder={searchPlaceholder} />
                    <CommandList>
                      <CommandEmpty>{emptyText}</CommandEmpty>
                      <CommandGroup>
                        {options.map((option) => (
                          <CommandItem
                            key={option.value}
                            value={option.label}
                            onSelect={() => {
                              field.onChange(
                                field.value === option.value ? '' : option.value
                              );
                              setOpen(false);
                            }}
                          >
                            <Check
                              className={cn(
                                'mr-2 h-4 w-4',
                                field.value === option.value
                                  ? 'opacity-100'
                                  : 'opacity-0'
                              )}
                            />
                            {option.label}
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
              {field.value && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-8 top-1/2 h-6 w-6 -translate-y-1/2 p-0 hover:bg-transparent"
                  onClick={(e) => {
                    e.stopPropagation();
                    field.onChange('');
                  }}
                >
                  <X className="h-4 w-4 opacity-50 hover:opacity-100" />
                </Button>
              )}
            </div>
          )}
        />
        {description ? (
          <p className="text-muted-foreground mt-1 text-xs">{description}</p>
        ) : null}
        <FieldError name={String(name)} />
      </div>
    );
  }

  // ---------- Custom controlled field ----------
  function FormCustom<N extends Name<Path<TFieldValues>>>(props: {
    name: N;
    children: (args: {
      value: TFieldValues[N];
      onChange: (value: TFieldValues[N]) => void;
    }) => React.ReactNode;
    rules?: RegisterOptions<TFieldValues, N>;
  }) {
    const { name, children, rules } = props;
    const { control } = useFormContext<TFieldValues>();

    return (
      <Controller
        name={name}
        control={control}
        rules={rules}
        render={({ field: { value, onChange } }) => (
          <>{children({ value, onChange })}</>
        )}
      />
    );
  }

  // ---------- Datetime input ----------
  function FormDatetime<N extends Name<Path<TFieldValues>>>(
    props: BaseFieldProps<TFieldValues, N> & {
      showTime?: boolean;
    }
  ) {
    const {
      name,
      label,
      placeholder,
      required,
      className,
      rules,
      description,
      id,
      showTime = false,
    } = props;
    const { control } = useFormContext<TFieldValues>();
    const htmlId = id ?? String(name);

    return (
      <div className={className}>
        {label && (
          <Label htmlFor={htmlId}>
            {label} {required ? '*' : null}
          </Label>
        )}
        <Controller
          name={name}
          control={control}
          rules={{ required: RequiredMessage(required), ...rules }}
          render={({ field }) => {
            const fieldValue = field.value as string | Date | undefined;
            const dateValue = fieldValue
              ? typeof fieldValue === 'string'
                ? new Date(fieldValue)
                : fieldValue
              : undefined;

            return (
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    id={htmlId}
                    variant="outline"
                    className={cn(
                      'mt-1 w-full justify-start text-left font-normal',
                      !dateValue && 'text-muted-foreground'
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {dateValue ? (
                      showTime ? (
                        format(dateValue, 'PPP p')
                      ) : (
                        format(dateValue, 'PPP')
                      )
                    ) : (
                      <span>{placeholder || 'Pick a date'}</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={dateValue}
                    onSelect={(date) => {
                      if (date) {
                        // If we have an existing time component and showTime is true, preserve it
                        if (showTime && dateValue) {
                          const hours = dateValue.getHours();
                          const minutes = dateValue.getMinutes();
                          date.setHours(hours, minutes);
                        }
                        field.onChange(date.toISOString());
                      } else {
                        field.onChange(undefined);
                      }
                    }}
                    initialFocus
                    captionLayout="dropdown"
                    fromYear={1920}
                    toYear={new Date().getFullYear()}
                  />
                  {showTime && (
                    <div className="border-t p-3">
                      <Label htmlFor={`${htmlId}-time`} className="text-xs">
                        Time
                      </Label>
                      <Input
                        id={`${htmlId}-time`}
                        type="time"
                        value={dateValue ? format(dateValue, 'HH:mm') : '00:00'}
                        onChange={(e) => {
                          const [hours, minutes] = e.target.value
                            .split(':')
                            .map(Number);
                          const newDate = dateValue
                            ? new Date(dateValue)
                            : new Date();
                          newDate.setHours(hours, minutes);
                          field.onChange(newDate.toISOString());
                        }}
                        className="mt-1"
                      />
                    </div>
                  )}
                </PopoverContent>
              </Popover>
            );
          }}
        />
        {description ? (
          <p className="text-muted-foreground mt-1 text-xs">{description}</p>
        ) : null}
        <FieldError name={String(name)} />
      </div>
    );
  }

  // ---------- Image upload ----------
  function FormImageUpload<N extends Name<Path<TFieldValues>>>(
    props: BaseFieldProps<TFieldValues, N> & {
      maxSizeMB?: number;
    }
  ) {
    const {
      name,
      label,
      required,
      className,
      rules,
      description,
      id,
      maxSizeMB = 10,
    } = props;
    const { control } = useFormContext<TFieldValues>();
    const htmlId = id ?? String(name);

    return (
      <div className={className}>
        {label && (
          <Label htmlFor={htmlId}>
            {label} {required ? '*' : null}
          </Label>
        )}
        <Controller
          name={name}
          control={control}
          rules={{ required: RequiredMessage(required), ...rules }}
          render={({ field: { value, onChange } }) => (
            <ImageUploadField
              value={value as string | null | undefined}
              onChange={onChange}
              maxSizeMB={maxSizeMB}
            />
          )}
        />
        {description ? (
          <p className="text-muted-foreground mt-1 text-xs">{description}</p>
        ) : null}
        <FieldError name={String(name)} />
      </div>
    );
  }

  function FormModal(props: {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    subTitle?: string | null;
    onSubmit: SubmitHandler<TFieldValues>;
    children: React.ReactNode;
    isSubmitting?: boolean;
    submitText?: string;
    defaultValues?: DefaultValues<TFieldValues>;
  }) {
    const {
      isOpen,
      onClose,
      title,
      subTitle,
      onSubmit,
      children,
      isSubmitting = false,
      submitText = 'Submit',
      defaultValues,
    } = props;

    const isMobile = useIsMobile();

    // Desktop: Dialog
    if (!isMobile) {
      return (
        <Dialog
          open={isOpen}
          onOpenChange={(open) => !open && !isSubmitting && onClose()}
        >
          <DialogContent className="flex max-h-[90vh] max-w-6xl flex-col">
            <DialogHeader>
              <DialogTitle>{title}</DialogTitle>
              {subTitle && <DialogDescription>{subTitle}</DialogDescription>}
            </DialogHeader>

            <Form
              onSubmit={onSubmit}
              defaultValues={defaultValues}
              className="flex min-h-0 flex-1 flex-col"
              mode="onSubmit"
            >
              <div className="flex-1 space-y-4 overflow-y-auto pr-2">
                {children}
              </div>

              <DialogFooter className="mb-0 flex-shrink-0 gap-3">
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex-1"
                >
                  {isSubmitting ? 'Please wait...' : submitText}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={onClose}
                  disabled={isSubmitting}
                  className="flex-1"
                >
                  Cancel
                </Button>
              </DialogFooter>
            </Form>
          </DialogContent>
        </Dialog>
      );
    }

    // Mobile: Drawer
    return (
      <Drawer
        open={isOpen}
        onOpenChange={(open) => !open && !isSubmitting && onClose()}
      >
        <DrawerContent className="flex max-h-[90vh] flex-col">
          <DrawerHeader className="flex-shrink-0 text-left">
            <DrawerTitle>{title}</DrawerTitle>
            {subTitle && <DrawerDescription>{subTitle}</DrawerDescription>}
          </DrawerHeader>

          <Form
            onSubmit={onSubmit}
            defaultValues={defaultValues}
            className="flex min-h-0 flex-1 flex-col"
            mode="onSubmit"
          >
            <div className="flex-1 space-y-4 overflow-y-auto px-4">
              {children}
            </div>

            <DrawerFooter className="flex flex-shrink-0 flex-row gap-3 border-t px-4 pt-3">
              <Button type="submit" disabled={isSubmitting} className="flex-1">
                {isSubmitting ? 'Please wait...' : submitText}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={isSubmitting}
                className="flex-1"
              >
                Cancel
              </Button>
            </DrawerFooter>
          </Form>
        </DrawerContent>
      </Drawer>
    );
  }

  function FormSheet(props: {
    isOpen: boolean;
    onOpenChange: (open: boolean) => void;
    title: string;
    subTitle?: string | null;
    onSubmit: SubmitHandler<TFieldValues>;
    children: React.ReactNode;
    isSubmitting?: boolean;
    submitText?: string;
    side?: 'top' | 'right' | 'bottom' | 'left';
    defaultValues?: DefaultValues<TFieldValues>;
  }) {
    const {
      isOpen,
      onOpenChange,
      title,
      subTitle,
      onSubmit,
      children,
      isSubmitting = false,
      submitText = 'Submit',
      side = 'right',
      defaultValues,
    } = props;

    return (
      <Sheet open={isOpen} onOpenChange={onOpenChange}>
        <SheetContent side={side} className="flex flex-col">
          <SheetHeader>
            <SheetTitle>{title}</SheetTitle>
            {subTitle && <SheetDescription>{subTitle}</SheetDescription>}
          </SheetHeader>

          <Form
            onSubmit={onSubmit}
            defaultValues={defaultValues}
            className="flex min-h-0 flex-1 flex-col"
          >
            <div className="flex-1 space-y-4 overflow-y-auto px-4">
              {children}
            </div>

            <SheetFooter className="mb-0 flex flex-row pt-0">
              <Button type="submit" disabled={isSubmitting} className="flex-1">
                {isSubmitting ? 'Please wait...' : submitText}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                className="flex-1"
              >
                Cancel
              </Button>
            </SheetFooter>
          </Form>
        </SheetContent>
      </Sheet>
    );
  }

  // ---------- Address input ----------
  function FormAddress<N extends Name<Path<TFieldValues>>>(props: {
    name: N;
    label?: string;
    description?: string;
    className?: string;
  }) {
    const { name, label = 'Address', description, className } = props;

    // Type assertion to handle path concatenation
    const field = (subfield: string) =>
      `${String(name)}.${subfield}` as Path<TFieldValues>;

    return (
      <div className={className}>
        <div className="space-y-4 rounded-lg border p-4">
          <div>
            <h4 className="text-sm font-medium">{label}</h4>
            {description && (
              <p className="text-muted-foreground mt-1 text-xs">
                {description}
              </p>
            )}
          </div>

          <FormString
            name={field('address1')}
            label="Street Address"
            placeholder="123 Main St"
            rules={{
              maxLength: {
                value: 255,
                message: 'Address cannot exceed 255 characters',
              },
            }}
          />

          <FormString
            name={field('address2')}
            label="Apt, Suite, etc."
            placeholder="Apt 4B"
            rules={{
              maxLength: {
                value: 255,
                message: 'Address line 2 cannot exceed 255 characters',
              },
            }}
          />

          <div className="grid grid-cols-2 gap-4">
            <FormString
              name={field('city')}
              label="City"
              placeholder="New York"
              rules={{
                maxLength: {
                  value: 100,
                  message: 'City cannot exceed 100 characters',
                },
              }}
            />
            <FormCombobox
              name={field('state')}
              label="State/Province"
              placeholder="Select state"
              searchPlaceholder="Search states..."
              options={US_STATE_OPTIONS}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <FormString
              name={field('zip')}
              label="ZIP/Postal Code"
              placeholder="10001"
              rules={{
                maxLength: {
                  value: 20,
                  message: 'ZIP/Postal code cannot exceed 20 characters',
                },
                pattern: {
                  value: /^[0-9-\s]*$/,
                  message:
                    'ZIP/Postal code should only contain numbers, hyphens, and spaces',
                },
              }}
            />
            <FormCombobox
              name={field('country')}
              label="Country"
              placeholder="Select country"
              searchPlaceholder="Search countries..."
              options={COUNTRY_OPTIONS}
            />
          </div>
        </div>
      </div>
    );
  }

  return {
    Form,
    FormString,
    FormEmail,
    FormNumber,
    FormText,
    FormSelect,
    FormCombobox,
    FormDatetime,
    FormImageUpload,
    FormCustom,
    FormModal,
    FormSheet,
    FormAddress,
  };
}
