'use client';

import { useState } from 'react';
import { Trash2, Eye } from 'lucide-react';
import Image from 'next/image';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface MediaItem {
  id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  status: string;
  view_url: string;
  thumbnail_url: string;
  mime_type: string;
}

interface MediaGalleryProps {
  media: MediaItem[];
  onDelete: (id: string) => void | Promise<void>;
}

export function MediaGallery({ media, onDelete }: MediaGalleryProps) {
  const [selectedMedia, setSelectedMedia] = useState<MediaItem | null>(null);

  const handleView = (item: MediaItem) => {
    setSelectedMedia(item);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this media?')) return;
    await onDelete(id);
  };

  if (media.length === 0) {
    return (
      <div className="text-muted-foreground py-12 text-center">
        <p>No media files uploaded yet</p>
      </div>
    );
  }
  console.log(media);

  return (
    <>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
        {media.map((item) => (
          <Card key={item.id} className="group relative overflow-hidden">
            <div className="bg-muted relative aspect-square">
              <div className="bg-muted flex h-full w-full items-center justify-center">
                <Image
                  src={item.thumbnail_url}
                  alt={item.file_name}
                  fill
                  className="object-cover"
                />
              </div>

              <div className="absolute inset-0 flex items-center justify-center gap-2 bg-black/60 opacity-0 transition-opacity group-hover:opacity-100">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleView(item)}
                >
                  <Eye className="h-4 w-4" />
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleDelete(item.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="p-3">
              <p className="truncate text-sm font-medium">{item.file_name}</p>
              <p className="text-muted-foreground text-xs">
                {(item.file_size / 1024 / 1024).toFixed(2)} MB •{' '}
                {item.file_type}
              </p>
            </div>
          </Card>
        ))}
      </div>

      <Dialog
        open={!!selectedMedia}
        onOpenChange={() => setSelectedMedia(null)}
      >
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>{selectedMedia?.file_name}</DialogTitle>
          </DialogHeader>
          {selectedMedia && (
            <div className="relative">
              {selectedMedia.file_type === 'image' ? (
                <Image
                  src={selectedMedia.view_url}
                  alt={selectedMedia.file_name}
                  width={1200}
                  height={800}
                  className="h-auto w-full"
                />
              ) : (
                <video controls className="w-full">
                  <source
                    src={selectedMedia.view_url}
                    type={selectedMedia.mime_type}
                  />
                  Your browser does not support the video tag.
                </video>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
