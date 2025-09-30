'use client';

import { use } from 'react';
import {
  ObjectHeader,
  ObjectActions,
  ObjectFields,
  ObjectParents,
  ObjectChildren,
} from '@/components/object-detail';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';

export default function RosterDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('roster', id);

  const handleActionClick = (action: string) => {
    console.log('Action clicked:', action, 'on roster member:', id);
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
