'use client';
import { ObjectActions } from '@/components/object-detail';
import { useHeader } from '@/components/header-provider';

export function DynamicPageActions() {
  console.log('DynamicPageActions rendered');
  const { headerData } = useHeader();
  if (!headerData?.actionsData) {
    return null;
  }

  console.log(
    'Rendering DynamicPageActions with actionsData:',
    headerData.actionsData
  );
  return (
    <div className="">
      <ObjectActions actionsData={headerData.actionsData} />
    </div>
  );
}
