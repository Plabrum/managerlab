import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { UserSchema } from '@/openapi/ariveAPI.schemas';
import { LogoutButton } from './logout-button';

export function UserSettingsCard({ user }: { user: UserSchema }) {
  return (
    <div className="container mx-auto space-y-6 p-6">
      <Card>
        <CardHeader>
          <CardTitle>Account Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div>
              <div className="text-muted-foreground text-sm font-medium">
                Name
              </div>
              <p className="text-sm">{user.name}</p>
            </div>
          </div>
          <div>
            <div>
              <div className="text-muted-foreground text-sm font-medium">
                Email
              </div>
              <p className="text-sm">{user.email}</p>
            </div>
          </div>
          <div>
            <div className="text-muted-foreground text-sm font-medium">
              Email Verified
            </div>
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
            <div className="text-muted-foreground text-sm font-medium">
              Account Status
            </div>
            <p className="text-sm">
              <Badge variant="outline">{user.state}</Badge>
            </p>
          </div>
          <div>
            <div className="text-muted-foreground text-sm font-medium">
              Member Since
            </div>
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
