'use client';

import { Suspense } from 'react';
import { MediaUpload } from '@/components/media/media-upload';
import { MediaGallery } from '@/components/media/media-gallery';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  useListObjectsSuspense,
  getListObjectsQueryKey,
} from '@/openapi/objects/objects';
import { useMediaIdDeleteMedia } from '@/openapi/media/media';
import { useQueryClient } from '@tanstack/react-query';
import type { ObjectListDTO } from '@/openapi/managerLab.schemas';

// Helper to extract media URLs and data from object fields
function extractMediaData(obj: ObjectListDTO) {
  const getField = (key: string) => {
    const field = obj.fields?.find((f) => f.key === key);
    if (!field?.value || typeof field.value !== 'object') return undefined;
    return 'value' in field.value ? field.value.value : undefined;
  };

  return {
    id: obj.id,
    file_name: getField('file_name') as string,
    file_type: getField('file_type') as string,
    file_size: getField('file_size') as number,
    status: getField('status') as string,
    view_url: getField('view_url') as string,
    thumbnail_url: getField('thumbnail_url') as string,
    mime_type: obj.subtitle?.split(' - ')[1] || '',
  };
}

const REQUEST_PARAMS = { limit: 100, offset: 0, filters: [], sorts: [] };

export default function MediaPage() {
  const queryClient = useQueryClient();
  const { data: response } = useListObjectsSuspense('media', REQUEST_PARAMS);
  const { mutateAsync: deleteMedia } = useMediaIdDeleteMedia();

  const media = response.objects.map(extractMediaData);

  const handleUploadComplete = () => {
    queryClient.invalidateQueries({
      queryKey: getListObjectsQueryKey('media', REQUEST_PARAMS),
    });
  };

  const handleDelete = async (id: string) => {
    await deleteMedia({ id });
    queryClient.invalidateQueries({
      queryKey: getListObjectsQueryKey('media', REQUEST_PARAMS),
    });
  };

  return (
    <div className="container mx-auto space-y-8 p-8">
      <div>
        <h1 className="mb-2 text-3xl font-bold">Media Library</h1>
        <p className="text-muted-foreground">
          Upload and manage your photos and videos
        </p>
      </div>

      <Tabs defaultValue="gallery" className="w-full">
        <TabsList>
          <TabsTrigger value="gallery">Gallery</TabsTrigger>
          <TabsTrigger value="upload">Upload</TabsTrigger>
        </TabsList>

        <TabsContent value="gallery" className="mt-6">
          <Suspense fallback={<div>Loading media...</div>}>
            <MediaGallery media={media} onDelete={handleDelete} />;
          </Suspense>
        </TabsContent>

        <TabsContent value="upload" className="mt-6">
          <MediaUpload onUploadComplete={handleUploadComplete} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
