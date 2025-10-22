'use client';
import { ObjectActions } from '@/components/object-detail';
import { useHeader } from '@/components/header-provider';

export function DynamicPageActions() {
  const { headerData } = useHeader();
  if (!headerData?.actionsData) {
    return null;
  }

  return (
    <div className="">
      <ObjectActions actionsData={headerData.actionsData} />
    </div>
  );
}
