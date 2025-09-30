'use client';

import { MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { ActionDTO } from '@/openapi/managerLab.schemas';

interface ActionsMenuProps {
  actions: ActionDTO[];
  onActionClick: (action: string) => void;
}

export function ActionsMenu({ actions, onActionClick }: ActionsMenuProps) {
  // Filter available actions
  const availableActions = actions.filter(
    (action) => action.available !== false
  );

  if (availableActions.length === 0) {
    return null;
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <MoreHorizontal className="h-5 w-5" />
          <span className="sr-only">Open menu</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {availableActions
          .sort((a, b) => (a.priority || 0) - (b.priority || 0))
          .map((action, index) => (
            <DropdownMenuItem
              key={`${action.action}-${index}`}
              onClick={() => onActionClick(action.action)}
              className="cursor-pointer"
            >
              {action.label}
            </DropdownMenuItem>
          ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
