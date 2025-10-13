'use client';

import { use, useEffect, useCallback } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import {
  ObjectHeader,
  ObjectActions,
  ObjectFields,
  ObjectParents,
  ObjectChildren,
} from '@/components/object-detail';
import { useOObjectTypeIdGetObjectDetailSuspense } from '@/openapi/objects/objects';
import { useBreadcrumb } from '@/components/breadcrumb-provider';
import { UpdatePostForm } from '@/components/actions/update-post-form';
import type {
  PostUpdateSchema,
  ActionDTO,
  ActionExecutionResponse,
} from '@/openapi/managerLab.schemas';
import type { ActionFormRenderer } from '@/hooks/use-action-executor';

export default function PostDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const pathname = usePathname();
  const router = useRouter();
  const { setBreadcrumb, clearBreadcrumb } = useBreadcrumb();

  const { data } = useOObjectTypeIdGetObjectDetailSuspense('posts', id);

  // Set breadcrumb title after data loads
  useEffect(() => {
    setBreadcrumb(pathname, data?.title);
    return () => {
      clearBreadcrumb(pathname);
    };
  }, [data?.title, pathname, setBreadcrumb, clearBreadcrumb]);

  // Handle action completion - redirect on delete
  const handleActionComplete = useCallback(
    (action: ActionDTO, response: ActionExecutionResponse) => {
      const isDeleteAction = action.action.toLowerCase().includes('delete');

      if (isDeleteAction && response.success) {
        router.push('/posts');
      }
    },
    [router]
  );

  // Custom form renderer for actions that require data
  const renderPostActionForm: ActionFormRenderer = useCallback(
    (props) => {
      const { action, onSubmit, onCancel, isSubmitting } = props;

      // Handle update action with custom form
      if (action.action === 'post_actions__post_update') {
        // Extract post data from fields for default values
        const defaultValues: Partial<PostUpdateSchema> = {
          title: data.title,
          // Add other fields as needed from data.fields
        };

        return (
          <UpdatePostForm
            defaultValues={defaultValues}
            onSubmit={(data) =>
              onSubmit({ action: 'post_actions__post_update', data })
            }
            onCancel={onCancel}
            isSubmitting={isSubmitting}
          />
        );
      }

      // Return null for actions that don't need custom forms
      // They will be executed automatically
      return null;
    },
    [data]
  );

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
            actionGroup="post_actions"
            objectId={id}
            renderActionForm={renderPostActionForm}
            onActionComplete={handleActionComplete}
          />
        </div>

        {/* Two Column Grid */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Left Column - Fields */}
          <ObjectFields fields={data.fields} />
        </div>

        {/* Parents */}
        <ObjectParents parents={data.parents || []} />

        {/* Children */}
        {data.children && <ObjectChildren items={data.children} />}
      </div>
    </div>
  );
}
