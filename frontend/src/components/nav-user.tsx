import { Building2, ChevronsUpDown, LogOut, User } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useAuth } from '@/components/providers/auth-provider';
import { ThemeSwitcher } from '@/components/theme-switcher';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar';
import { useAuthLogoutLogoutUser } from '@/openapi/auth/auth';

export function NavUser({
  user,
}: {
  user: {
    name: string;
    email: string;
    avatar: string;
  };
}) {
  const { isMobile } = useSidebar();
  const navigate = useNavigate();
  const [isSigningOut, setIsSigningOut] = useState(false);

  const authContext = useAuth();
  const currentUser = authContext.user;
  const { teams } = authContext;

  const { mutate: logout } = useAuthLogoutLogoutUser({
    mutation: {
      onSuccess: () => {
        navigate({ to: '/', replace: true });
      },
      onError: (error) => {
        console.error('Logout failed:', error);
        navigate({ to: '/', replace: true });
      },
      onSettled: () => {
        setIsSigningOut(false);
      },
    },
  });

  const handleLogout = () => {
    setIsSigningOut(true);
    logout();
  };

  // Get current team's id for navigation
  const currentTeam = teams.find((t) => t.is_selected);
  const teamId = currentTeam?.id as string | undefined;

  const handleUserSettings = () => {
    navigate({ to: `/settings/user/${currentUser.id}` });
  };

  const handleTeamSettings = () => {
    if (teamId) {
      navigate({ to: `/settings/team/${teamId}` });
    }
  };

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            >
              <Avatar className="h-8 w-8 rounded-lg">
                <AvatarImage src={user.avatar} alt={user.name} />
                <AvatarFallback className="rounded-lg">
                  {user.name.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-medium">{user.name}</span>
                <span className="truncate text-xs">{user.email}</span>
              </div>
              <ChevronsUpDown className="ml-auto size-4" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
            side={isMobile ? 'bottom' : 'right'}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                <Avatar className="h-8 w-8 rounded-lg">
                  <AvatarImage src={user.avatar} alt={user.name} />
                  <AvatarFallback className="rounded-lg">
                    {user.name.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-medium">{user.name}</span>
                  <span className="truncate text-xs">{user.email}</span>
                </div>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuGroup>
              <DropdownMenuItem onClick={handleUserSettings}>
                <User />
                User Settings
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleTeamSettings} disabled={!teamId}>
                <Building2 />
                Team Settings
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <div className="flex justify-center px-2 py-2">
              <ThemeSwitcher />
            </div>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} disabled={isSigningOut}>
              <LogOut />
              {isSigningOut ? 'Logging out...' : 'Log out'}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
