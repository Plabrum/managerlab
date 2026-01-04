import * as React from 'react';
import { format } from 'date-fns';
import { CalendarIcon, Upload, X, Image as ImageIcon } from 'lucide-react';
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
import { useMediaUpload } from '@/hooks/useMediaUpload';
import { cn } from '@/lib/utils'; // optional: your className helper
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

/**
 * Reusable image upload field component
 * Handles file selection, preview, upload to S3, and registration
 */
function ImageUploadField({
  value,
  onChange,
  accept = 'image/*',
  maxSizeMB = 10,
}: {
  value?: string | null;
  onChange: (mediaId: string | null) => void;
  accept?: string;
  maxSizeMB?: number;
}) {
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const [preview, setPreview] = React.useState<string | null>(null);
  const { uploadFile, status, progress } = useMediaUpload();

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    // Validate file size
    const fileSizeMB = file.size / 1024 / 1024;
    if (fileSizeMB > maxSizeMB) {
      alert(`File size must be less than ${maxSizeMB}MB`);
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Upload file
    await uploadFile(file, {
      autoRegister: true,
      onSuccess: (result) => {
        onChange(result.mediaId);
      },
    });
  };

  const handleRemove = () => {
    setPreview(null);
    onChange(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="mt-1 space-y-4 rounded-lg border p-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">
          {preview || value ? 'Image' : 'Upload Image'}
        </h4>
        {(preview || value) && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleRemove}
            disabled={status === 'uploading' || status === 'registering'}
          >
            <X className="h-4 w-4" />
            Remove
          </Button>
        )}
      </div>

      <div className="flex items-center gap-4">
        {/* Preview */}
        <div className="bg-muted flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden rounded-lg border">
          {preview ? (
            <img
              src={preview}
              alt="Preview"
              className="h-full w-full object-cover"
            />
          ) : value ? (
            <div className="flex flex-col items-center justify-center gap-1 text-center">
              <ImageIcon className="text-muted-foreground h-6 w-6" />
              <span className="text-muted-foreground text-xs">Current</span>
            </div>
          ) : (
            <ImageIcon className="text-muted-foreground h-8 w-8" />
          )}
        </div>

        {/* Upload Button */}
        <div className="flex-1">
          <input
            ref={fileInputRef}
            type="file"
            accept={accept}
            onChange={handleFileSelect}
            className="hidden"
          />
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={status === 'uploading' || status === 'registering'}
          >
            <Upload className="mr-2 h-4 w-4" />
            {preview || value ? 'Change Image' : 'Choose File'}
          </Button>
          <p className="text-muted-foreground mt-2 text-xs">
            {status === 'uploading' && `Uploading... ${progress}%`}
            {status === 'registering' && 'Processing...'}
            {status === 'complete' && preview && 'Upload complete'}
            {status === 'idle' && `Max ${maxSizeMB}MB`}
          </p>
        </div>
      </div>
    </div>
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
    return (
      <FormProvider {...methods}>
        <form
          onSubmit={methods.handleSubmit(onSubmit)}
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
      accept?: string;
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
      accept = 'image/*',
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
              accept={accept}
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

  return {
    Form,
    FormString,
    FormEmail,
    FormText,
    FormSelect,
    FormDatetime,
    FormImageUpload,
    FormCustom,
    FormModal,
    FormSheet,
  };
}
