import { Mail, User, CheckCircle2, XCircle, Shield } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { UserAndRoleSchema, RoleLevel } from '@/openapi/ariveAPI.schemas';

function getRoleDisplay(roleLevel: RoleLevel): string {
  const roleMap: Record<RoleLevel, string> = {
    owner: 'Owner',
    admin: 'Admin',
    member: 'Member',
    viewer: 'Viewer',
  };
  return roleMap[roleLevel] || roleLevel;
}

function getRoleVariant(
  roleLevel: RoleLevel
): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (roleLevel) {
    case 'owner':
      return 'default';
    case 'admin':
      return 'secondary';
    case 'member':
    case 'viewer':
      return 'outline';
    default:
      return 'outline';
  }
}

export function TeamMembersCard({ users }: { users: UserAndRoleSchema[] }) {
  return (
    <div className="container mx-auto space-y-6 p-6">
      <Card>
        <CardHeader>
          <CardTitle>Team Members ({users.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {users.length === 0 ? (
            <p className="text-muted-foreground py-8 text-center text-sm">
              No team members found
            </p>
          ) : (
            <div className="space-y-4">
              {users.map((user) => (
                <div
                  key={String(user.id)}
                  className="hover:bg-accent/50 flex items-start justify-between rounded-lg border p-4 transition-colors"
                >
                  <div className="flex flex-1 items-start gap-3">
                    <div className="bg-primary/10 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full">
                      <User className="text-primary h-5 w-5" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="mb-1 flex items-center gap-2">
                        <h4 className="truncate text-sm font-medium">
                          {user.name}
                        </h4>
                        <Badge
                          variant={getRoleVariant(user.role_level)}
                          className="text-xs"
                        >
                          <Shield className="mr-1 h-3 w-3" />
                          {getRoleDisplay(user.role_level)}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {user.state}
                        </Badge>
                      </div>
                      <div className="text-muted-foreground mb-2 flex items-center gap-2 text-sm">
                        <Mail className="h-3 w-3 flex-shrink-0" />
                        <span className="truncate">{user.email}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {user.email_verified ? (
                          <div className="flex items-center gap-1 text-xs text-green-600">
                            <CheckCircle2 className="h-3 w-3" />
                            <span>Email verified</span>
                          </div>
                        ) : (
                          <div className="text-muted-foreground flex items-center gap-1 text-xs">
                            <XCircle className="h-3 w-3" />
                            <span>Email not verified</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
