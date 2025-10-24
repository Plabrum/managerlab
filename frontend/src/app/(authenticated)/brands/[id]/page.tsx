'use client';

import { use } from 'react';
import { ObjectActions } from '@/components/object-detail';
import { BrandFields } from '@/components/brand-detail';
import { useBrandsIdGetBrandSuspense } from '@/openapi/brands/brands';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType } from '@/openapi/managerLab.schemas';

export default function BrandDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data, refetch } = useBrandsIdGetBrandSuspense(id);

  return (
    <PageTopBar
      title={data.name}
      state="active"
      actions={
        <ObjectActions
          data={data}
          actionGroup={ActionGroupType.brand_actions}
          onRefetch={refetch}
        />
      }
    >
      <div className="space-y-6">
        {/* Two Column Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Left Column - Fields */}
          <BrandFields brand={data} />
        </div>
      </div>
    </PageTopBar>
  );
}
