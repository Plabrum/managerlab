'use client';

import { useState, useCallback } from 'react';
import { X, Loader2, CheckCircle2, UploadIcon } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Dropzone, DropzoneEmptyState } from '@/components/ui/dropzone';
import {
  mediaPresignedUploadRequestPresignedUpload,
  mediaRegisterRegisterMedia,
} from '@/openapi/media/media';

interface UploadedFile {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'processing' | 'complete' | 'error';
  progress: number;
  error?: string;
  mediaId?: string;
}

export function MediaUpload({
  onUploadComplete,
}: {
  onUploadComplete?: () => void;
}) {
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const uploadFile = async (uploadFile: UploadedFile) => {
    try {
      // Update status to uploading
      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? { ...f, status: 'uploading', progress: 10 }
            : f
        )
      );

      // Step 1: Request presigned URL from backend
      const presignedResponse =
        await mediaPresignedUploadRequestPresignedUpload({
          file_name: uploadFile.file.name,
          content_type: uploadFile.file.type,
        });

      setFiles((prev) =>
        prev.map((f) => (f.id === uploadFile.id ? { ...f, progress: 30 } : f))
      );

      // Step 2: Upload directly to S3 using presigned URL
      const uploadResponse = await fetch(presignedResponse.upload_url, {
        method: 'PUT',
        body: uploadFile.file,
        headers: {
          'Content-Type': uploadFile.file.type,
        },
      });

      if (!uploadResponse.ok) {
        throw new Error('Upload to S3 failed');
      }

      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? { ...f, progress: 70, status: 'processing' }
            : f
        )
      );

      // Step 3: Register the file with backend (triggers thumbnail generation)
      const mediaResponse = await mediaRegisterRegisterMedia({
        file_key: presignedResponse.file_key,
        file_name: uploadFile.file.name,
        file_size: uploadFile.file.size,
        mime_type: uploadFile.file.type,
      });

      // Update to complete
      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? {
                ...f,
                status: 'complete',
                progress: 100,
                mediaId: mediaResponse.id,
              }
            : f
        )
      );

      onUploadComplete?.();
    } catch (error) {
      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadFile.id
            ? {
                ...f,
                status: 'error',
                error: error instanceof Error ? error.message : 'Upload failed',
              }
            : f
        )
      );
    }
  };

  const handleDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
      id: Math.random().toString(36).substring(7),
      file,
      status: 'pending',
      progress: 0,
    }));

    setFiles((prev) => [...prev, ...newFiles]);

    // Start uploading each file
    newFiles.forEach((file) => {
      uploadFile(file);
    });
  }, []);

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  return (
    <div className="space-y-4">
      <Dropzone
        onDrop={handleDrop}
        accept={{
          'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
          'video/*': ['.mp4', '.mov', '.avi', '.webm'],
        }}
        maxFiles={10}
      >
        <DropzoneEmptyState>
          <div className="flex flex-col items-center justify-center">
            <div className="bg-muted text-muted-foreground flex size-12 items-center justify-center rounded-md">
              <UploadIcon size={24} />
            </div>
            <p className="my-2 text-lg font-medium">Upload media files</p>
            <p className="text-muted-foreground text-sm">
              Drag and drop or click to upload
            </p>
            <p className="text-muted-foreground mt-1 text-xs">
              Accepts images and videos
            </p>
          </div>
        </DropzoneEmptyState>
      </Dropzone>

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file) => (
            <Card key={file.id} className="p-4">
              <div className="flex items-center justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">
                    {file.file.name}
                  </p>
                  <p className="text-muted-foreground text-xs">
                    {(file.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  {file.status === 'uploading' ||
                  file.status === 'processing' ? (
                    <Loader2 className="text-primary h-4 w-4 animate-spin" />
                  ) : file.status === 'complete' ? (
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                  ) : null}

                  {file.status !== 'complete' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(file.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>

              {(file.status === 'uploading' ||
                file.status === 'processing') && (
                <div className="mt-2">
                  <Progress value={file.progress} className="h-2" />
                  <p className="text-muted-foreground mt-1 text-xs">
                    {file.status === 'uploading'
                      ? 'Uploading...'
                      : 'Processing...'}
                  </p>
                </div>
              )}

              {file.status === 'error' && (
                <p className="text-destructive mt-2 text-xs">{file.error}</p>
              )}

              {file.status === 'complete' && (
                <p className="mt-2 text-xs text-green-600">Upload complete!</p>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
