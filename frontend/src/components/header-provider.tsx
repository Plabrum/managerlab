'use client';

import { createContext, useContext, useState, useCallback } from 'react';
import type {
  ActionDTO,
  ActionGroupType,
  ObjectDetailDTO,
} from '@/openapi/managerLab.schemas';

interface HeaderData {
  title: string;
  state: string;
  createdAt: string;
  updatedAt: string;
  actions?: ActionDTO[];
  actionGroup?: ActionGroupType;
  objectId?: string;
  objectData?: ObjectDetailDTO;
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
