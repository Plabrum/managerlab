import * as React from 'react';
import { Building2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { handleError } from '@/lib/error-handler';
import { useTeamsCreateTeam } from '@/openapi/teams/teams';

export function OnboardingPage() {
  const [formData, setFormData] = React.useState({
    name: '',
    description: '',
  });

  const createTeamMutation = useTeamsCreateTeam({
    mutation: {
      onSuccess: () => {
        // Redirect to dashboard with full page reload to refresh server-side data
        window.location.href = '/dashboard';
      },
      onError: (error) => {
        handleError(error, { fallbackMessage: 'Failed to create team' });
      },
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    createTeamMutation.mutate({ data: formData });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-900 via-black to-gray-900 p-4">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-white">
            <Building2 className="h-8 w-8 text-black" />
          </div>
          <h1 className="text-3xl font-bold text-white">Welcome to Arive</h1>
          <p className="mt-2 text-gray-400">
            Let&apos;s get started by creating your first team
          </p>
        </div>

        {/* Form Card */}
        <div className="rounded-lg border border-gray-800 bg-gray-900 p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-white">
                Team name
              </Label>
              <Input
                id="name"
                placeholder="e.g., Acme Inc."
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                required
                disabled={createTeamMutation.isPending}
                className="border-gray-700 bg-gray-800 text-white placeholder:text-gray-500"
              />
              <p className="text-xs text-gray-500">
                This will be your workspace for managing campaigns and roster
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description" className="text-white">
                Description <span className="text-gray-500">(optional)</span>
              </Label>
              <Textarea
                id="description"
                placeholder="Brief description of your team..."
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                disabled={createTeamMutation.isPending}
                rows={3}
                className="border-gray-700 bg-gray-800 text-white placeholder:text-gray-500"
              />
            </div>

            <Button
              type="submit"
              disabled={createTeamMutation.isPending || !formData.name}
              className="w-full"
            >
              {createTeamMutation.isPending
                ? 'Creating your team...'
                : 'Create team'}
            </Button>
          </form>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-gray-500">
          You can invite team members and add more teams later
        </p>
      </div>
    </div>
  );
}
