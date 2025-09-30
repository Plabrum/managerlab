'use client';

import { use, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import {
  ObjectHeader,
  ObjectActions,
  ObjectFields,
  ObjectParents,
  ObjectChildren,
} from '@/components/object-detail';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { useBreadcrumb } from '@/components/breadcrumb-provider';

export default function UserDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const pathname = usePathname();
  const { setBreadcrumb, clearBreadcrumb } = useBreadcrumb();

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('users', id);

  // Set breadcrumb title after data loads
  useEffect(() => {
    setBreadcrumb(pathname, data?.title);
    return () => {
      clearBreadcrumb(pathname);
    };
  }, [data?.title, pathname, setBreadcrumb, clearBreadcrumb]);

  const handleActionClick = (action: string) => {
    console.log('Action clicked:', action, 'on user:', id);
    // TODO: Implement action handlers
  };

  return (
    <div className="container mx-auto py-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <ObjectHeader
            title={data.title}
            state={data.state}
            createdAt={data.created_at}
            updatedAt={data.updated_at}
          />
          <ObjectActions
            actions={data.actions}
            onActionClick={handleActionClick}
          />
        </div>

        {/* Fields */}
        <ObjectFields fields={data.fields} />

        {/* Parents */}
        <ObjectParents parents={data.parents || []} />

        {/* Children */}
        {data.children && <ObjectChildren items={data.children} />}
      </div>
    </div>
  );
}
