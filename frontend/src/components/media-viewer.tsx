import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Image } from '@/components/ui/image';

interface MediaViewerProps {
  url: string;
  alt?: string;
}

export function MediaViewer({ url, alt }: MediaViewerProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  return (
    <>
      <Card>
        <CardContent className="p-6">
          <div
            className="bg-muted aspect-video w-full cursor-pointer overflow-hidden rounded-lg border"
            onClick={() => setIsFullscreen(true)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                setIsFullscreen(true);
              }
            }}
            role="button"
            tabIndex={0}
            aria-label="Open media in fullscreen"
          >
            <Image
              src={url}
              alt={alt || 'Media preview'}
              className="h-full w-full object-contain"
            />
          </div>
        </CardContent>
      </Card>

      {/* Fullscreen Dialog */}
      <Dialog open={isFullscreen} onOpenChange={setIsFullscreen}>
        <DialogContent className="h-[90vh] w-full max-w-7xl">
          <DialogHeader>
            <DialogTitle>{alt || 'Image'}</DialogTitle>
            <DialogDescription>
              Click outside or press ESC to close
            </DialogDescription>
          </DialogHeader>
          <div className="flex-1 overflow-auto">
            <Image
              src={url}
              alt={alt || 'Full size image'}
              className="h-auto w-full"
            />
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
