'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useBreadcrumb } from '@/components/breadcrumb-provider';
import { useHeader, type ActionData } from '@/components/header-provider';

interface DetailPageLayoutProps {
  children: React.ReactNode;
  title: string;
  state: string;
  actionsData?: ActionData;
  createdAt?: string;
  updatedAt?: string;
}

export function DetailPageLayout({
  children,
  title,
  state,
  actionsData,
}: DetailPageLayoutProps) {
  const pathname = usePathname();
  const { setBreadcrumb, clearBreadcrumb } = useBreadcrumb();
  const { setHeaderData } = useHeader();

  // Set breadcrumb title when data loads
  useEffect(() => {
    setBreadcrumb(pathname, title);
    return () => {
      clearBreadcrumb(pathname);
    };
  }, [title, pathname, setBreadcrumb, clearBreadcrumb]);

  // Set header data when page loads
  useEffect(() => {
    setHeaderData({
      title,
      state,
      actionsData,
    });
    return () => {
      setHeaderData(null);
    };
  }, [title, state, actionsData, setHeaderData]);

  return <>{children}</>;
}
