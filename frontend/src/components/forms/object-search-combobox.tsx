'use client';

import * as React from 'react';
import { Check, ChevronsUpDown, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { useListObjects } from '@/openapi/objects/objects';
import { useActionsActionGroupExecuteAction } from '@/openapi/actions/actions';
import type {
  ObjectTypes,
  ActionGroupType,
} from '@/openapi/managerLab.schemas';
import { Label } from '@/components/ui/label';
import { useQueryClient } from '@tanstack/react-query';

interface ObjectSearchComboboxProps {
  /** The type of object to search for (brands, campaigns, etc.) */
  objectType: ObjectTypes;
  /** The currently selected object ID (SQID string) */
  value: string | null;
  /** Callback when selection changes (receives SQID string) */
  onValueChange: (id: string | null) => void;
  /** Optional label for the field */
  label?: string;
  /** Custom placeholder text */
  placeholder?: string;
  /** Disable the combobox */
  disabled?: boolean;
  /** Enable inline creation (default: true) */
  allowCreate?: boolean;
  /** Custom label for create action */
  createLabel?: string;
  /** Show required asterisk */
  required?: boolean;
  /** Description text below the field */
  description?: string;
  /** Custom className */
  className?: string;
}

/**
 * Map object types to their action groups and create actions
 */
const OBJECT_CREATE_ACTIONS: Record<
  ObjectTypes,
  { actionGroup: ActionGroupType; action: string } | null
> = {
  brands: {
    actionGroup: 'top_level_brand_actions',
    action: 'top_level_brand_actions__brand_create',
  },
  campaigns: {
    actionGroup: 'top_level_campaign_actions',
    action: 'top_level_campaign_actions__campaign_create',
  },
  roster: {
    actionGroup: 'top_level_roster_actions',
    action: 'top_level_roster_actions__top_level_roster_create',
  },
  media: {
    actionGroup: 'top_level_media_actions',
    action: 'top_level_media_actions__top_level_media_create',
  },
  documents: {
    actionGroup: 'top_level_document_actions',
    action: 'top_level_document_actions__top_level_document_create',
  },
  deliverables: {
    actionGroup: 'top_level_deliverable_actions',
    action: 'top_level_deliverable_actions__top_level_deliverable_create',
  },
  deliverablemedia: null, // No create action defined
  brandcontacts: null, // No create action defined
  invoices: null, // No create action defined
  users: null, // No create action defined
  teams: null, // No create action defined
};

/**
 * A searchable combobox for selecting objects with optional inline creation
 *
 * Features:
 * - Client-side search/filtering
 * - Automatic inline creation when no matches found
 * - Type-safe with auto-generated schemas
 * - Reusable across all object types
 * - Handles cache invalidation automatically
 *
 * @example
 * ```tsx
 * <ObjectSearchCombobox
 *   objectType="brands"
 *   value={brandId}
 *   onValueChange={setBrandId}
 *   label="Brand"
 *   required
 * />
 * ```
 */
export function ObjectSearchCombobox({
  objectType,
  value,
  onValueChange,
  label,
  placeholder,
  disabled = false,
  allowCreate = true,
  createLabel,
  required = false,
  description,
  className,
}: ObjectSearchComboboxProps) {
  const [open, setOpen] = React.useState(false);
  const [searchValue, setSearchValue] = React.useState('');
  const [isCreating, setIsCreating] = React.useState(false);

  const queryClient = useQueryClient();
  const createMutation = useActionsActionGroupExecuteAction();

  // Fetch objects - uses client-side filtering for now
  const { data, isLoading } = useListObjects(objectType, {
    offset: 0,
    limit: 100, // Start with 100, can be increased or switched to server-side later
    sorts: [],
    filters: [],
  });

  // Memoize objects array to prevent useMemo dependency issues
  const objects = React.useMemo(() => data?.objects || [], [data?.objects]);

  // Find the selected object to display its title
  const selectedObject = value ? objects.find((obj) => obj.id === value) : null;

  // Filter objects based on search
  const filteredObjects = React.useMemo(() => {
    if (!searchValue.trim()) return objects;

    const search = searchValue.toLowerCase();
    return objects.filter((obj) => obj.title.toLowerCase().includes(search));
  }, [objects, searchValue]);

  // Get the create action config for this object type
  const createActionConfig = OBJECT_CREATE_ACTIONS[objectType];

  // Check if we should show the "create new" option
  const showCreateNew =
    allowCreate &&
    createActionConfig &&
    searchValue.trim() &&
    !filteredObjects.some(
      (obj) => obj.title.toLowerCase() === searchValue.toLowerCase()
    );

  /**
   * Handle inline creation of new object
   */
  const handleCreateNew = async () => {
    if (!createActionConfig || !searchValue.trim()) return;

    setIsCreating(true);
    try {
      // Determine the field name based on object type
      // Most use 'name', campaigns use 'name', etc.
      const fieldName =
        objectType === 'brands'
          ? 'name'
          : objectType === 'campaigns'
            ? 'name'
            : objectType === 'roster'
              ? 'name'
              : 'title';

      const result = await createMutation.mutateAsync({
        actionGroup: createActionConfig.actionGroup,
        data: {
          action: createActionConfig.action,
          data: { [fieldName]: searchValue.trim() },
        } as unknown as Parameters<
          typeof createMutation.mutateAsync
        >[0]['data'],
      });

      // Backend returns ActionExecutionResponse with a redirect to the new object
      // Extract the ID from the redirect path
      let newId: string | null = null;
      if (
        result.action_result &&
        result.action_result.type === 'redirect' &&
        'path' in result.action_result
      ) {
        // Extract ID from path like "/brands/abc123" -> "abc123"
        const pathParts = result.action_result.path.split('/');
        newId = pathParts[pathParts.length - 1];
      }

      if (!newId) {
        throw new Error('Failed to extract ID from create action response');
      }

      // Invalidate cache so the list refreshes
      await queryClient.invalidateQueries({
        queryKey: [`/o/${objectType}`],
      });

      // Select the newly created object
      onValueChange(newId);
      setOpen(false);
      setSearchValue('');
    } catch (error) {
      console.error(`Failed to create new ${objectType}:`, error);
      // Error handling could be improved with toast notifications
    } finally {
      setIsCreating(false);
    }
  };

  const handleSelect = (selectedId: string) => {
    onValueChange(selectedId === value ? null : selectedId);
    setOpen(false);
    setSearchValue('');
  };

  // Generate user-friendly labels
  const typeLabel =
    objectType.charAt(0).toUpperCase() + objectType.slice(1, -1); // "brands" -> "Brand"
  const defaultPlaceholder =
    placeholder || `Select ${typeLabel.toLowerCase()}...`;
  const defaultCreateLabel =
    createLabel || `Create new ${typeLabel.toLowerCase()}`;

  return (
    <div className={className}>
      {label && (
        <Label>
          {label} {required && <span className="text-destructive">*</span>}
        </Label>
      )}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            disabled={disabled}
            className={cn(
              'mt-1 w-full justify-between',
              !value && 'text-muted-foreground'
            )}
          >
            {isLoading
              ? 'Loading...'
              : selectedObject
                ? selectedObject.title
                : defaultPlaceholder}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent
          className="w-[var(--radix-popover-trigger-width)] p-0"
          align="start"
        >
          <Command shouldFilter={false}>
            <CommandInput
              placeholder={`Search ${typeLabel.toLowerCase()}...`}
              value={searchValue}
              onValueChange={setSearchValue}
            />
            <CommandList>
              <CommandEmpty>
                {isLoading
                  ? 'Loading...'
                  : `No ${typeLabel.toLowerCase()} found.`}
              </CommandEmpty>
              {filteredObjects.length > 0 && (
                <CommandGroup>
                  {filteredObjects.map((obj) => (
                    <CommandItem
                      key={obj.id}
                      value={obj.id}
                      onSelect={handleSelect}
                    >
                      <Check
                        className={cn(
                          'mr-2 h-4 w-4',
                          value === obj.id ? 'opacity-100' : 'opacity-0'
                        )}
                      />
                      {obj.title}
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}
              {showCreateNew && (
                <CommandGroup>
                  <CommandItem
                    onSelect={handleCreateNew}
                    disabled={isCreating}
                    className="text-primary"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    {isCreating
                      ? 'Creating...'
                      : `${defaultCreateLabel}: "${searchValue}"`}
                  </CommandItem>
                </CommandGroup>
              )}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
      {description && (
        <p className="text-muted-foreground mt-1 text-xs">{description}</p>
      )}
    </div>
  );
}
