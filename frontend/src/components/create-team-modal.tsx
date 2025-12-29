import * as React from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useAuth } from '@/components/providers/auth-provider';
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
import { Textarea } from '@/components/ui/textarea';
import { config } from '@/lib/config';

interface CreateTeamModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateTeamModal({ open, onOpenChange }: CreateTeamModalProps) {
  const { refetchTeams } = useAuth();
  const navigate = useNavigate();
  const [isCreating, setIsCreating] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [formData, setFormData] = React.useState({
    name: '',
    description: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsCreating(true);

    try {
      const res = await fetch(`${config.api.baseUrl}/teams`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        // Refetch teams to update the list
        await refetchTeams();
        // Reset form
        setFormData({ name: '', description: '' });
        // Close modal
        onOpenChange(false);
        // Refresh server components without full page reload
      } else {
        const errorData = await res.json();
        setError(errorData.detail || 'Failed to create team');
      }
    } catch {
      setError('An error occurred while creating the team');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create a new team</DialogTitle>
          <DialogDescription>
            Add a new team to organize your campaigns and roster.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Team name</Label>
              <Input
                id="name"
                placeholder="Acme Inc."
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
                disabled={isCreating}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="description">Description (optional)</Label>
              <Textarea
                id="description"
                placeholder="Brief description of your team..."
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                disabled={isCreating}
                rows={3}
              />
            </div>
            {error && (
              <div className="bg-destructive/15 text-destructive rounded-md p-3 text-sm">
                {error}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isCreating}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isCreating || !formData.name}>
              {isCreating ? 'Creating...' : 'Create team'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
