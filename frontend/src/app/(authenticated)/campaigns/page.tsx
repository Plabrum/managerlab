'use client';

import * as React from 'react';
import { DataTable } from '@/components/data-table/data-table';
import { useListObjectsSuspense } from '@/openapi/objects/objects';
import type { ObjectListRequest } from '@/openapi/managerLab.schemas';

export default function CampaignsPage() {
  const [request, setRequest] = React.useState<ObjectListRequest>({
    limit: 10,
    offset: 0,
    filters: [],
    sorts: [],
  });

  const { data } = useListObjectsSuspense('campaigns', request);

  const handleRequestChange = (newRequest: ObjectListRequest) => {
    setRequest(newRequest);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Campaigns</h1>
        <p className="text-muted-foreground">
          Manage and view all your campaigns
        </p>
      </div>

      <DataTable
        data={data}
        onRequestChange={handleRequestChange}
        loading={false}
      />
    </div>
  );
}
