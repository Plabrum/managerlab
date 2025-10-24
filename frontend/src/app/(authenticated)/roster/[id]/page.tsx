'use client';

import { use } from 'react';
import { ObjectActions } from '@/components/object-detail';
import { RosterFields } from '@/components/roster-detail';
import { useRosterIdGetRosterSuspense } from '@/openapi/roster/roster';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/managerLab.schemas';

export default function RosterDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data, refetch } = useRosterIdGetRosterSuspense(id);

  return (
    <PageTopBar
      title={data.name}
      state={data.state}
      actions={
        <ObjectActions
          data={data}
          actionGroup={ActionGroupType.roster_actions}
          onRefetch={refetch}
        />
      }
    >
      <div className="space-y-6">
        {/* Two Column Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Left Column - Fields */}
          <RosterFields roster={data} />
        </div>
      </div>
    </PageTopBar>
  );
}
