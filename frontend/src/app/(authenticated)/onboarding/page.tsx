'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { config } from '@/lib/config';
import { Building2 } from 'lucide-react';

export default function OnboardingPage() {
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

    console.log('[Onboarding] Submitting form with data:', formData);

    try {
      const res = await fetch(`${config.api.baseUrl}/users/teams`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(formData),
      });

      console.log('[Onboarding] Response status:', res.status);
      console.log('[Onboarding] Response ok:', res.ok);

      if (res.ok) {
        const teamData = await res.json();
        console.log('[Onboarding] Team created:', teamData);

        // Redirect to dashboard with full page reload to refresh server-side data
        console.log('[Onboarding] Redirecting to dashboard...');
        window.location.href = '/dashboard';
      } else {
        const errorData = await res.json();
        console.log('[Onboarding] Error response:', errorData);
        setError(errorData.detail || 'Failed to create team');
        setIsCreating(false);
      }
    } catch (err) {
      console.error('[Onboarding] Exception:', err);
      setError('An error occurred while creating the team');
      setIsCreating(false);
    }
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
                disabled={isCreating}
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
                disabled={isCreating}
                rows={3}
                className="border-gray-700 bg-gray-800 text-white placeholder:text-gray-500"
              />
            </div>

            {error && (
              <div className="rounded-md border border-red-900/50 bg-red-900/20 p-3 text-sm text-red-400">
                {error}
              </div>
            )}

            <Button
              type="submit"
              disabled={isCreating || !formData.name}
              className="w-full"
            >
              {isCreating ? 'Creating your team...' : 'Create team'}
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
