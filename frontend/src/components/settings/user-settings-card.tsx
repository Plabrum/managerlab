'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { UserSchema } from '@/openapi/managerLab.schemas';
import { LogoutButton } from './logout-button';

export function UserSettingsCard({ user }: { user: UserSchema }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-muted-foreground text-sm font-medium">
              Name
            </label>
            <p className="text-sm">{user.name}</p>
          </div>
          <div>
            <label className="text-muted-foreground text-sm font-medium">
              Email
            </label>
            <p className="text-sm">{user.email}</p>
          </div>
          <div>
            <label className="text-muted-foreground text-sm font-medium">
              Email Verified
            </label>
            <p className="text-sm">
              {user.email_verified ? (
                <Badge variant="default" className="bg-green-500">
                  Verified
                </Badge>
              ) : (
                <Badge variant="secondary">Not Verified</Badge>
              )}
            </p>
          </div>
          <div>
            <label className="text-muted-foreground text-sm font-medium">
              Account Status
            </label>
            <p className="text-sm">
              <Badge variant="outline">{user.state}</Badge>
            </p>
          </div>
          <div>
            <label className="text-muted-foreground text-sm font-medium">
              Member Since
            </label>
            <p className="text-sm">
              {new Date(user.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Session</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4 text-sm">
            Sign out of your account on this device.
          </p>
          <LogoutButton />
        </CardContent>
      </Card>
    </div>
  );
}
