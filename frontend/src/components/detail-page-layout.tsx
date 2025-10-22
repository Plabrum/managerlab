'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useBreadcrumb } from '@/components/breadcrumb-provider';
import { useHeader } from '@/components/header-provider';
import type {
  ActionDTO,
  ActionGroupType,
  ObjectDetailDTO,
} from '@/openapi/managerLab.schemas';

interface DetailPageLayoutProps {
  children: React.ReactNode;
  title: string;
  state: string;
  createdAt: string;
  updatedAt: string;
  actions?: ActionDTO[];
  actionGroup?: ActionGroupType;
  objectId?: string;
  objectData?: ObjectDetailDTO;
}

export function DetailPageLayout({
  children,
  title,
  state,
  createdAt,
  updatedAt,
  actions,
  actionGroup,
  objectId,
  objectData,
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
      createdAt,
      updatedAt,
      actions,
      actionGroup,
      objectId,
      objectData,
    });
    return () => {
      setHeaderData(null);
    };
  }, [
    title,
    state,
    createdAt,
    updatedAt,
    actions,
    actionGroup,
    objectId,
    objectData,
    setHeaderData,
  ]);

  return <>{children}</>;
}
