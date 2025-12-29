import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import {
  Settings,
  Plus,
  Save,
  Star,
  StarOff,
  Trash2,
  Columns3,
} from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { getErrorMessage } from '@/lib/error-handler';
import {
  useViewsObjectTypeCreateSavedView,
  useViewsObjectTypeIdUpdateSavedView,
  useViewsObjectTypeIdDeleteSavedView,
} from '@/openapi/views/views';
import { ColumnVisibilityDialog } from './column-visibility-dialog';
import { ViewModeSelector } from './view-mode-selector';
import type {
  SavedViewSchema,
  SavedViewConfigSchema,
  ObjectTypes,
  ColumnDefinitionSchema,
} from '@/openapi/ariveAPI.schemas';
import type { ViewMode } from '@/types/view-modes';
import type { VisibilityState } from '@tanstack/react-table';

interface SavedViewSettingsProps {
  objectType: ObjectTypes;
  currentView: SavedViewSchema;
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
  hasUnsavedChanges: boolean;
  currentConfig: SavedViewConfigSchema;
  onViewSelect?: (id: unknown | null) => void;
  columns: ColumnDefinitionSchema[];
  columnVisibility: VisibilityState;
  onColumnVisibilityChange: (visibility: VisibilityState) => void;
}

export function SavedViewSettings({
  objectType,
  currentView,
  viewMode,
  onViewModeChange,
  hasUnsavedChanges,
  currentConfig,
  onViewSelect,
  columns,
  columnVisibility,
  onColumnVisibilityChange,
}: SavedViewSettingsProps) {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [showColumnsDialog, setShowColumnsDialog] = useState(false);
  const [newViewName, setNewViewName] = useState('');
  const [isPersonal, setIsPersonal] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [popoverOpen, setPopoverOpen] = useState(false);

  const queryClient = useQueryClient();

  // Mutations
  const createViewMutation = useViewsObjectTypeCreateSavedView();
  const updateViewMutation = useViewsObjectTypeIdUpdateSavedView();
  const deleteViewMutation = useViewsObjectTypeIdDeleteSavedView();

  // Handle creating a new view
  const handleCreateView = async () => {
    if (!newViewName.trim()) {
      toast.error('Please enter a view name');
      return;
    }

    setIsCreating(true);
    try {
      await createViewMutation.mutateAsync({
        objectType,
        data: {
          name: newViewName.trim(),
          object_type: objectType,
          config: currentConfig,
          is_personal: isPersonal,
          is_default: false,
        },
      });

      // Refetch views list to show new view immediately
      await queryClient.refetchQueries({
        queryKey: [`/views/${objectType}`],
      });

      toast.success(`View "${newViewName}" created successfully`);
      setShowCreateDialog(false);
      setNewViewName('');
      setIsPersonal(true);
      setPopoverOpen(false);
    } catch (err) {
      toast.error(getErrorMessage(err, 'Failed to create view'));
    } finally {
      setIsCreating(false);
    }
  };

  // Handle updating current view
  const handleUpdateView = async () => {
    if (!currentView.id) {
      toast.error('Cannot update the default view');
      return;
    }

    try {
      await updateViewMutation.mutateAsync({
        objectType,
        id: currentView.id,
        data: {
          config: currentConfig,
        },
      });

      // Refetch views list and detail
      await queryClient.refetchQueries({
        queryKey: [`/views/${objectType}`],
      });
      await queryClient.refetchQueries({
        queryKey: [`/views/${objectType}/${currentView.id}`],
      });

      toast.success(`View "${currentView.name}" updated successfully`);
      setPopoverOpen(false);
    } catch (err) {
      toast.error(getErrorMessage(err, 'Failed to update view'));
    }
  };

  // Handle setting view as default
  const handleSetDefault = async () => {
    if (!currentView.id) {
      toast.error('Cannot set default on the fallback view');
      return;
    }

    if (!currentView.is_personal) {
      toast.error('Only personal views can be set as default');
      return;
    }

    try {
      await updateViewMutation.mutateAsync({
        objectType,
        id: currentView.id,
        data: {
          is_default: true,
        },
      });

      // Refetch views list and default view
      await queryClient.refetchQueries({
        queryKey: [`/views/${objectType}`],
      });
      await queryClient.refetchQueries({
        queryKey: [`/views/${objectType}/default`],
      });

      toast.success(`"${currentView.name}" set as default`);
      setPopoverOpen(false);
    } catch (err) {
      toast.error(getErrorMessage(err, 'Failed to set default view'));
    }
  };

  // Handle unsetting view as default
  const handleUnsetDefault = async () => {
    if (!currentView.id) return;

    try {
      await updateViewMutation.mutateAsync({
        objectType,
        id: currentView.id,
        data: {
          is_default: false,
        },
      });

      // Refetch views list and default view
      await queryClient.refetchQueries({
        queryKey: [`/views/${objectType}`],
      });
      await queryClient.refetchQueries({
        queryKey: [`/views/${objectType}/default`],
      });

      toast.success(`"${currentView.name}" unset as default`);
      setPopoverOpen(false);
    } catch (err) {
      toast.error(getErrorMessage(err, 'Failed to unset default view'));
    }
  };

  // Handle deleting a view
  const handleDeleteView = async () => {
    if (!currentView.id) return;

    setIsDeleting(true);
    try {
      await deleteViewMutation.mutateAsync({
        objectType,
        id: currentView.id,
      });

      // Refetch views list
      await queryClient.refetchQueries({
        queryKey: [`/views/${objectType}`],
      });

      // Refetch default view (user will fall back to it)
      await queryClient.refetchQueries({
        queryKey: [`/views/${objectType}/default`],
      });

      toast.success(`View "${currentView.name}" deleted`);
      setShowDeleteDialog(false);
      setPopoverOpen(false);

      // Switch to default view after deletion
      onViewSelect?.(null);
    } catch (err) {
      toast.error(getErrorMessage(err, 'Failed to delete view'));
    } finally {
      setIsDeleting(false);
    }
  };

  const canUpdate =
    currentView.id && currentView.is_personal && hasUnsavedChanges;
  const canSetDefault =
    currentView.id && currentView.is_personal && !currentView.is_default;
  const canUnsetDefault =
    currentView.id && currentView.is_personal && currentView.is_default;
  const canDelete = currentView.id && currentView.is_personal;

  return (
    <>
      <Popover open={popoverOpen} onOpenChange={setPopoverOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" size="icon">
            <Settings className="h-4 w-4" />
          </Button>
        </PopoverTrigger>
        <PopoverContent align="end" className="w-64">
          <div className="space-y-4">
            {/* View Mode Selector */}
            <div className="space-y-2">
              <div className="text-muted-foreground text-xs font-medium">
                View Mode
              </div>
              <ViewModeSelector value={viewMode} onChange={onViewModeChange} />
            </div>

            <Separator />

            {/* Manage Columns Button (only for table view) */}
            {viewMode === 'table' && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={() => {
                    setShowColumnsDialog(true);
                    setPopoverOpen(false);
                  }}
                >
                  <Columns3 className="mr-2 h-4 w-4" />
                  Manage Columns
                </Button>
                <Separator />
              </>
            )}

            {/* View Actions */}
            <div className="space-y-1">
              <Button
                variant="ghost"
                size="sm"
                className="w-full justify-start"
                onClick={() => {
                  setShowCreateDialog(true);
                  setPopoverOpen(false);
                }}
              >
                <Plus className="mr-2 h-4 w-4" />
                Save as New View
              </Button>

              {canUpdate ? (
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={handleUpdateView}
                >
                  <Save className="mr-2 h-4 w-4" />
                  Update &quot;{String(currentView.name)}&quot;
                </Button>
              ) : null}

              {canSetDefault ? (
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={handleSetDefault}
                >
                  <Star className="mr-2 h-4 w-4" />
                  Set as Default
                </Button>
              ) : null}

              {canUnsetDefault ? (
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start"
                  onClick={handleUnsetDefault}
                >
                  <StarOff className="mr-2 h-4 w-4" />
                  Unset Default
                </Button>
              ) : null}

              {canDelete ? (
                <>
                  <Separator className="my-1" />
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive hover:text-destructive w-full justify-start"
                    onClick={() => {
                      setShowDeleteDialog(true);
                      setPopoverOpen(false);
                    }}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete View
                  </Button>
                </>
              ) : null}
            </div>
          </div>
        </PopoverContent>
      </Popover>

      {/* Create View Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Save as New View</DialogTitle>
            <DialogDescription>
              Create a new saved view with the current settings
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="view-name">View Name</Label>
              <Input
                id="view-name"
                placeholder="e.g., Active Roster"
                value={newViewName}
                onChange={(e) => setNewViewName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && newViewName.trim()) {
                    handleCreateView();
                  }
                }}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="is-personal" className="flex flex-col gap-1">
                <span>Personal View</span>
                <span className="text-muted-foreground text-xs font-normal">
                  {isPersonal
                    ? 'Only you can see this view'
                    : 'All team members can see this view'}
                </span>
              </Label>
              <Switch
                id="is-personal"
                checked={isPersonal}
                onCheckedChange={setIsPersonal}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowCreateDialog(false);
                setNewViewName('');
                setIsPersonal(true);
              }}
              disabled={isCreating}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreateView}
              disabled={isCreating || !newViewName.trim()}
            >
              {isCreating ? 'Creating...' : 'Create View'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete View</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &quot;{currentView.name}&quot;?
              This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDeleteDialog(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteView}
              disabled={isDeleting}
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Column Visibility Dialog */}
      <ColumnVisibilityDialog
        columns={columns}
        columnVisibility={columnVisibility}
        onColumnVisibilityChange={onColumnVisibilityChange}
        open={showColumnsDialog}
        onOpenChange={setShowColumnsDialog}
      />
    </>
  );
}
