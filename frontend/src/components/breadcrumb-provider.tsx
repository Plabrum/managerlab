'use client';

import { createContext, useContext, useState, useCallback } from 'react';

interface BreadcrumbContextValue {
  breadcrumbs: Map<string, string>;
  setBreadcrumb: (path: string, title: string) => void;
  clearBreadcrumb: (path: string) => void;
}

const BreadcrumbContext = createContext<BreadcrumbContextValue | undefined>(
  undefined
);

export function BreadcrumbProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [breadcrumbs, setBreadcrumbs] = useState<Map<string, string>>(
    new Map()
  );

  const setBreadcrumb = useCallback((path: string, title: string) => {
    setBreadcrumbs((prev) => {
      const next = new Map(prev);
      next.set(path, title);
      return next;
    });
  }, []);

  const clearBreadcrumb = useCallback((path: string) => {
    setBreadcrumbs((prev) => {
      const next = new Map(prev);
      next.delete(path);
      return next;
    });
  }, []);

  return (
    <BreadcrumbContext.Provider
      value={{ breadcrumbs, setBreadcrumb, clearBreadcrumb }}
    >
      {children}
    </BreadcrumbContext.Provider>
  );
}

export function useBreadcrumb() {
  const context = useContext(BreadcrumbContext);
  if (context === undefined) {
    throw new Error('useBreadcrumb must be used within a BreadcrumbProvider');
  }
  return context;
}
