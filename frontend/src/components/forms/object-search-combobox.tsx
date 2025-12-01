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
import {
  useActionsActionGroupExecuteAction,
  useActionsActionGroupObjectIdExecuteObjectAction,
} from '@/openapi/actions/actions';
import type {
  ObjectTypes,
  ActionGroupType,
  ActionDTO,
} from '@/openapi/ariveAPI.schemas';
import { Label } from '@/components/ui/label';
import { executeActionApi } from '@/hooks/action-executor/execute-action-api';
import { useQueryClient } from '@tanstack/react-query';
import { handleQueryInvalidation } from '@/hooks/action-executor/handle-query-invalidation';

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
    actionGroup: 'brand_actions',
    action: 'brand_actions__brand_create',
  },
  campaigns: {
    actionGroup: 'campaign_actions',
    action: 'campaign_actions__campaign_create',
  },
  roster: {
    actionGroup: 'roster_actions',
    action: 'roster_actions__roster_create',
  },
  media: {
    actionGroup: 'media_actions',
    action: 'media_actions__media_register',
  },
  documents: {
    actionGroup: 'document_actions',
    action: 'document_actions__document_register',
  },
  deliverables: {
    actionGroup: 'deliverable_actions',
    action: 'deliverable_actions__deliverable_create',
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
 * - Inline creation when no matches found
 * - Type-safe with auto-generated schemas
 * - Reusable across all object types
 * - Automatic query invalidation via backend response
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
  const executeGroupActionMutation = useActionsActionGroupExecuteAction();
  const executeObjectActionMutation =
    useActionsActionGroupObjectIdExecuteObjectAction();

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

  // Show create button if allowed and action is configured
  const showCreateButton = allowCreate && createActionConfig;

  // Disable create if no search value or if exact match exists
  const isCreateDisabled =
    !searchValue.trim() ||
    filteredObjects.some(
      (obj) => obj.title.toLowerCase() === searchValue.toLowerCase()
    );

  /**
   * Handle inline creation of new object
   */
  const handleCreateNew = async () => {
    if (!createActionConfig || !searchValue.trim()) return;

    setIsCreating(true);
    try {
      // Create a minimal ActionDTO for the create action
      const action: ActionDTO = {
        action: createActionConfig.action,
        label: 'Create',
        action_group_type: createActionConfig.actionGroup,
        is_bulk_allowed: false,
        available: true,
        priority: 0,
      };

      const result = await executeActionApi({
        action,
        actionGroup: createActionConfig.actionGroup,
        actionBody: {
          action: createActionConfig.action,
          data: { name: searchValue.trim() },
        },
        executeGroupActionMutation,
        executeObjectActionMutation,
      });

      // Backend returns the new object's ID in created_id
      const newId = result.created_id as string | null | undefined;
      if (!newId) {
        throw new Error('Failed to get ID from create action response');
      }

      // Handle query invalidation from backend response
      handleQueryInvalidation(queryClient, result);

      // Wait for the query to refetch so the new object appears in the list
      await queryClient.refetchQueries({
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
              {showCreateButton && (
                <CommandGroup>
                  <CommandItem
                    onSelect={handleCreateNew}
                    disabled={isCreating || isCreateDisabled}
                    className="text-primary"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    {isCreating
                      ? 'Creating...'
                      : searchValue.trim()
                        ? `${defaultCreateLabel}: "${searchValue}"`
                        : defaultCreateLabel}
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
