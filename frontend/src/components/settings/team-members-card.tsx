import { Mail, CheckCircle2, XCircle, Shield } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import {
  CardRow,
  CardRowAvatar,
  CardRowContent,
  CardRowDescription,
  CardRowLeft,
  CardRowRight,
  CardRowTitle,
} from '@/components/ui/card-row';
import {
  CardRowList,
  CardRowListEmpty,
  CardRowListHeader,
} from '@/components/ui/card-row-list';
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

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function TeamMembersCard({ users }: { users: UserAndRoleSchema[] }) {
  return (
    <div className="mx-auto max-w-7xl space-y-6 p-8">
      <CardRowListHeader
        title="Team Members"
        description={`${users.length} ${users.length === 1 ? 'member' : 'members'} in your team`}
      />

      {users.length === 0 ? (
        <CardRowListEmpty
          title="No team members yet"
          description="Invite members to collaborate"
        />
      ) : (
        <CardRowList>
          {users.map((user) => (
            <CardRow key={String(user.id)}>
              <CardRowLeft>
                <CardRowAvatar>
                  <span className="text-primary text-base font-semibold tracking-tight">
                    {getInitials(user.name)}
                  </span>
                </CardRowAvatar>

                <CardRowContent>
                  <CardRowTitle>{user.name}</CardRowTitle>
                  <CardRowDescription>
                    <div className="flex items-center gap-2">
                      <Mail className="h-3.5 w-3.5 flex-shrink-0 opacity-60" />
                      <span className="truncate">{user.email}</span>
                    </div>
                  </CardRowDescription>
                </CardRowContent>
              </CardRowLeft>

              <CardRowRight>
                {user.email_verified ? (
                  <div className="flex items-center gap-1.5 text-sm text-green-600">
                    <CheckCircle2 className="h-4 w-4" />
                    <span className="hidden sm:inline">Verified</span>
                  </div>
                ) : (
                  <div className="text-muted-foreground flex items-center gap-1.5 text-sm">
                    <XCircle className="h-4 w-4" />
                    <span className="hidden sm:inline">Unverified</span>
                  </div>
                )}

                <Badge variant="outline" className="text-xs font-normal">
                  {user.state}
                </Badge>

                <Badge
                  variant={getRoleVariant(user.role_level)}
                  className="gap-1.5"
                >
                  <Shield className="h-3.5 w-3.5" />
                  {getRoleDisplay(user.role_level)}
                </Badge>
              </CardRowRight>
            </CardRow>
          ))}
        </CardRowList>
      )}
    </div>
  );
}
