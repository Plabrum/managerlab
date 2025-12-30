import * as React from 'react';
import { TooltipProvider } from '@/components/ui/tooltip';
import { useKeyboardShortcut } from '@/hooks/use-keyboard-shortcut';
import { useIsMobile } from '@/hooks/use-mobile';
import { getCookie, setCookie } from '@/lib/cookies';
import { cn } from '@/lib/utils';

const SIDEBAR_COOKIE_NAME = 'sidebar_state';
const SIDEBAR_COOKIE_MAX_AGE = 60 * 60 * 24 * 7;
const SIDEBAR_WIDTH = '16rem';
const SIDEBAR_WIDTH_ICON = '3rem';

export { SIDEBAR_WIDTH, SIDEBAR_WIDTH_ICON };

export type SidebarContextProps = {
  state: 'expanded' | 'collapsed';
  open: boolean;
  setOpen: (open: boolean) => void;
  openMobile: boolean;
  setOpenMobile: (open: boolean) => void;
  isMobile: boolean;
  toggleSidebar: () => void;
};

const SidebarContext = React.createContext<SidebarContextProps | null>(null);

export function useSidebar() {
  const context = React.useContext(SidebarContext);
  if (!context) {
    throw new Error('useSidebar must be used within a SidebarProvider.');
  }
  return context;
}

// Desktop provider: Handles collapsible state with cookie persistence
function DesktopSidebarProvider({
  defaultOpen = true,
  open: openProp,
  onOpenChange: setOpenProp,
  className,
  style,
  children,
  ...props
}: React.ComponentProps<'div'> & {
  defaultOpen?: boolean;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}) {
  const [internalOpen, setInternalOpen] = React.useState<boolean>(() => {
    const cookieValue = getCookie(SIDEBAR_COOKIE_NAME);
    return cookieValue !== 'false';
  });

  const open = openProp !== undefined ? openProp : internalOpen;

  const setOpen = React.useCallback(
    (value: boolean | ((value: boolean) => boolean)) => {
      const newOpen = typeof value === 'function' ? value(open) : value;

      if (openProp === undefined) {
        setInternalOpen(newOpen);
      }

      setOpenProp?.(newOpen);

      setCookie(SIDEBAR_COOKIE_NAME, String(newOpen), {
        maxAge: SIDEBAR_COOKIE_MAX_AGE,
      });
    },
    [open, openProp, setOpenProp]
  );

  const toggleSidebar = React.useCallback(() => {
    setOpen((prev) => !prev);
  }, [setOpen]);

  useKeyboardShortcut({ key: 'b', meta: true }, toggleSidebar);

  const state = open ? 'expanded' : 'collapsed';

  const contextValue = React.useMemo<SidebarContextProps>(
    () => ({
      state,
      open,
      setOpen,
      isMobile: false,
      openMobile: false,
      setOpenMobile: () => {},
      toggleSidebar,
    }),
    [state, open, setOpen, toggleSidebar]
  );

  return (
    <SidebarContext.Provider value={contextValue}>
      <TooltipProvider delayDuration={0}>
        <div
          data-slot="sidebar-wrapper"
          style={
            {
              '--sidebar-width': SIDEBAR_WIDTH,
              '--sidebar-width-icon': SIDEBAR_WIDTH_ICON,
              ...style,
            } as React.CSSProperties
          }
          className={cn(
            'group/sidebar-wrapper has-data-[variant=inset]:bg-sidebar flex min-h-svh w-full',
            className
          )}
          {...props}
        >
          {children}
        </div>
      </TooltipProvider>
    </SidebarContext.Provider>
  );
}

// Mobile provider: Simple Sheet overlay state
function MobileSidebarProvider({
  className,
  style,
  children,
  ...props
}: React.ComponentProps<'div'>) {
  const [openMobile, setOpenMobile] = React.useState(false);

  const toggleSidebar = React.useCallback(() => {
    setOpenMobile((prev) => !prev);
  }, []);

  const contextValue = React.useMemo<SidebarContextProps>(
    () => ({
      state: 'expanded',
      open: true,
      setOpen: () => {},
      isMobile: true,
      openMobile,
      setOpenMobile,
      toggleSidebar,
    }),
    [openMobile, toggleSidebar]
  );

  return (
    <SidebarContext.Provider value={contextValue}>
      <TooltipProvider delayDuration={0}>
        <div
          data-slot="sidebar-wrapper"
          style={
            {
              '--sidebar-width': SIDEBAR_WIDTH,
              '--sidebar-width-icon': SIDEBAR_WIDTH_ICON,
              ...style,
            } as React.CSSProperties
          }
          className={cn(
            'group/sidebar-wrapper has-data-[variant=inset]:bg-sidebar flex min-h-svh w-full',
            className
          )}
          {...props}
        >
          {children}
        </div>
      </TooltipProvider>
    </SidebarContext.Provider>
  );
}

// Main provider: Routes to mobile or desktop based on screen size
export function SidebarProvider(
  props: React.ComponentProps<'div'> & {
    defaultOpen?: boolean;
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
  }
) {
  const isMobile = useIsMobile();

  return isMobile ? (
    <MobileSidebarProvider {...props} />
  ) : (
    <DesktopSidebarProvider {...props} />
  );
}
