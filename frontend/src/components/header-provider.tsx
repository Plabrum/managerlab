'use client';

import { createContext, useContext, useState, useCallback } from 'react';
import type { QueryClient } from '@tanstack/react-query';
import type {
  ActionDTO,
  ActionGroupType,
  ActionExecutionResponse,
  ObjectDetailDTO,
} from '@/openapi/managerLab.schemas';

export interface ActionData {
  actions: ActionDTO[];
  actionGroup: ActionGroupType;
  objectId: string;
  objectData?: ObjectDetailDTO;
  onInvalidate?: (
    queryClient: QueryClient,
    action: ActionDTO,
    response: ActionExecutionResponse
  ) => void;
  onActionComplete?: (
    action: ActionDTO,
    response: ActionExecutionResponse
  ) => void;
}

export interface HeaderData {
  title: string;
  state?: string;
  actionsData?: ActionData;
}

interface HeaderContextValue {
  headerData: HeaderData | null;
  setHeaderData: (data: HeaderData | null) => void;
}

const HeaderContext = createContext<HeaderContextValue | undefined>(undefined);

export function HeaderProvider({ children }: { children: React.ReactNode }) {
  const [headerData, setHeaderData] = useState<HeaderData | null>(null);

  const handleSetHeaderData = useCallback((data: HeaderData | null) => {
    setHeaderData(data);
  }, []);

  return (
    <HeaderContext.Provider
      value={{ headerData, setHeaderData: handleSetHeaderData }}
    >
      {children}
    </HeaderContext.Provider>
  );
}

export function useHeader() {
  const context = useContext(HeaderContext);
  if (context === undefined) {
    throw new Error('useHeader must be used within a HeaderProvider');
  }
  return context;
}
