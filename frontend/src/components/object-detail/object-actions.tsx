'use client';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal } from 'lucide-react';
import type { ActionDTO } from '@/openapi/managerLab.schemas';

interface ObjectActionsProps {
  actions: ActionDTO[];
  onActionClick?: (action: string) => void;
}

export function ObjectActions({ actions, onActionClick }: ObjectActionsProps) {
  const availableActions = actions.filter(
    (action) => action.available !== false
  );

  if (availableActions.length === 0) {
    return null;
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm">
          <MoreHorizontal className="mr-2 h-4 w-4" />
          Actions
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {availableActions
          .sort((a, b) => (a.priority || 0) - (b.priority || 0))
          .map((action, index) => (
            <DropdownMenuItem
              key={`${action.action}-${index}`}
              onClick={() => onActionClick?.(action.action)}
              className="cursor-pointer"
            >
              {action.label}
            </DropdownMenuItem>
          ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
