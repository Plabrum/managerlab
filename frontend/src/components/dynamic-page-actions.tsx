'use client';
import { ObjectActions } from '@/components/object-detail';
import { useHeader } from '@/components/header-provider';

export function DynamicPageActions() {
  const { headerData } = useHeader();
  if (!headerData) {
    return null;
  }

  const { actions, actionGroup, objectId, objectData } = headerData;

  return (
    <div className="">
      {actions && actionGroup && objectId && (
        <ObjectActions
          actions={actions}
          actionGroup={actionGroup}
          objectId={objectId}
          objectData={objectData}
        />
      )}
    </div>
  );
}
