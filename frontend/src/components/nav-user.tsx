'use client';

import {
  Building2,
  ChevronsUpDown,
  LogOut,
  User,
  Monitor,
  Moon,
  Sun,
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';

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
import { useAuth } from '@/components/providers/auth-provider';

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
  const router = useRouter();
  const [isSigningOut, setIsSigningOut] = useState(false);
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  const authContext = useAuth();
  const currentUser = authContext.user;
  const { teams, currentTeamId } = authContext;

  // Avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  const { mutate: logout } = useAuthLogoutLogoutUser({
    mutation: {
      onSuccess: () => {
        router.push('/');
        router.refresh();
      },
      onError: (error) => {
        console.error('Logout failed:', error);
        router.push('/');
        router.refresh();
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

  // Get current team's public_id for navigation
  const currentTeam = teams.find((t) => t.team_id === currentTeamId);
  const teamPublicId = currentTeam?.public_id;

  const handleUserSettings = () => {
    router.push(`/settings/user/${currentUser.id}`);
  };

  const handleTeamSettings = () => {
    if (teamPublicId) {
      router.push(`/settings/team/${teamPublicId}`);
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
              <DropdownMenuItem
                onClick={handleTeamSettings}
                disabled={!teamPublicId}
              >
                <Building2 />
                Team Settings
              </DropdownMenuItem>
            </DropdownMenuGroup>
            <DropdownMenuSeparator />
            <DropdownMenuLabel className="p-0 font-normal">
              <div className="text-muted-foreground px-2 py-1.5 text-xs">
                Theme
              </div>
            </DropdownMenuLabel>
            <DropdownMenuGroup>
              <DropdownMenuItem
                onClick={() => setTheme('light')}
                disabled={!mounted}
              >
                <Sun />
                <span className="flex-1">Light</span>
                {mounted && theme === 'light' && (
                  <span className="text-muted-foreground text-xs">✓</span>
                )}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => setTheme('dark')}
                disabled={!mounted}
              >
                <Moon />
                <span className="flex-1">Dark</span>
                {mounted && theme === 'dark' && (
                  <span className="text-muted-foreground text-xs">✓</span>
                )}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => setTheme('system')}
                disabled={!mounted}
              >
                <Monitor />
                <span className="flex-1">System</span>
                {mounted && theme === 'system' && (
                  <span className="text-muted-foreground text-xs">✓</span>
                )}
              </DropdownMenuItem>
            </DropdownMenuGroup>
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
