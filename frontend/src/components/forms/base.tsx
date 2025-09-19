import * as React from 'react';
import {
  useForm,
  FormProvider,
  useFormContext,
  type FieldValues,
  type Path,
  type RegisterOptions,
  type SubmitHandler,
} from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils'; // optional: your className helper
import { Modal } from '../modal';
import { Button } from '../ui/button';

type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};

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

function RequiredMessage(required?: boolean | string) {
  if (!required) return undefined;
  return typeof required === 'string' ? required : 'This field is required';
}

function FieldError({ name }: { name: string }) {
  const {
    formState: { errors },
  } = useFormContext();
  const err = (errors as any)?.[name];
  if (!err) return null;
  return (
    <p className="mt-1 text-sm text-red-400">
      {String(err.message ?? 'Invalid value')}
    </p>
  );
}

export function createTypedForm<TFieldValues extends FieldValues>() {
  type Name<N extends Path<TFieldValues>> = N;

  // ---------- Form wrapper ----------
  function Form(props: {
    defaultValues?: DeepPartial<TFieldValues>;
    onSubmit: SubmitHandler<TFieldValues>;
    className?: string;
    children: React.ReactNode;
    mode?: Parameters<typeof useForm>[0]['mode'];
    reValidateMode?: Parameters<typeof useForm>[0]['reValidateMode'];
    resolver?: Parameters<typeof useForm<TFieldValues>>[0]['resolver'];
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
    console.log('Rendering Form', defaultValues);
    const methods = useForm<TFieldValues>({
      defaultValues: defaultValues as any,
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
    } = props;
    const { register } = useFormContext<TFieldValues>();
    const htmlId = id ?? String(name);

    return (
      <div className={className}>
        {label && (
          <Label htmlFor={htmlId} className="text-zinc-300">
            {label} {required ? '*' : null}
          </Label>
        )}
        <Input
          id={htmlId}
          type="text"
          autoFocus={autoFocus}
          {...register(name, {
            required: RequiredMessage(required),
            ...rules,
          })}
          className="mt-1 border-zinc-700 bg-zinc-800 text-white placeholder:text-zinc-500"
          placeholder={placeholder}
        />
        {description ? (
          <p className="mt-1 text-xs text-zinc-400">{description}</p>
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
          <Label htmlFor={htmlId} className="text-zinc-300">
            {label} {required ? '*' : null}
          </Label>
        )}
        <Input
          id={htmlId}
          type="email"
          {...register(name, {
            required: RequiredMessage(required),
            pattern: defaultEmailPattern,
            ...(rules as any),
          })}
          className="mt-1 border-zinc-700 bg-zinc-800 text-white placeholder:text-zinc-500"
          placeholder={placeholder}
        />
        {description ? (
          <p className="mt-1 text-xs text-zinc-400">{description}</p>
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
          <Label htmlFor={htmlId} className="text-zinc-300">
            {label} {required ? '*' : null}
          </Label>
        )}
        <Textarea
          id={htmlId}
          {...register(name, {
            required: RequiredMessage(required),
            ...(rules as any),
          })}
          className={cn(
            'mt-1 border-zinc-700 bg-zinc-800 text-white placeholder:text-zinc-500',
            !resize && 'resize-none'
          )}
          placeholder={placeholder}
          rows={rows}
        />
        {description ? (
          <p className="mt-1 text-xs text-zinc-400">{description}</p>
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
    } = props;

    return (
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        title={title}
        subTitle={subTitle}
      >
        <Form onSubmit={onSubmit} className="w-full space-y-4" mode="onSubmit">
          {children}

          <div className="flex gap-3 pt-6">
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-white text-black hover:bg-zinc-200 disabled:opacity-50"
            >
              {isSubmitting ? 'Please wait...' : submitText}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1 border-zinc-700 bg-transparent text-zinc-300 hover:bg-zinc-800 hover:text-white"
            >
              Cancel
            </Button>
          </div>
        </Form>
      </Modal>
    );
  }
  return { Form, FormString, FormEmail, FormText, FormModal };
}
