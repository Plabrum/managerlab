'use client';

import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Dropzone, DropzoneEmptyState } from '@/components/ui/dropzone';
import { useState, useCallback, useEffect } from 'react';
import { toast } from 'sonner';
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  UploadIcon,
  X,
} from 'lucide-react';
import { mediaPresignedUploadRequestPresignedUpload } from '@/openapi/media/media';
import { RegisterMediaSchema } from '@/openapi/managerLab.schemas';
import { Image } from '@/components/ui/image';

// interface MediaUploadData {
//   file_key: string;
//   file_name: string;
//   file_size: number;
//   mime_type: string;
//   file_type: string;
// }

interface CreateMediaFormProps {
  onSubmit: (data: RegisterMediaSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

type UploadStatus = 'idle' | 'uploading' | 'complete' | 'error';

/**
 * Form for uploading media to S3
 * Handles: file selection → presigned URL request → S3 upload
 * Calls onSubmit with file_key for the consumer to handle registration
 */
export function CreateMediaForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: CreateMediaFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      setUploadStatus('idle');
      setProgress(0);
      setError(null);

      // Create preview URL for images
      if (file.type.startsWith('image/')) {
        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
      } else {
        setPreviewUrl(null);
      }
    }
  }, []);

  const removeFile = () => {
    // Clean up preview URL
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setUploadStatus('idle');
    setProgress(0);
    setError(null);
    setPreviewUrl(null);
  };

  // Clean up preview URL on unmount
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedFile) {
      toast.error('Please select a file');
      return;
    }

    try {
      // Step 1: Request presigned URL from backend
      setUploadStatus('uploading');
      setProgress(10);

      const presignedResponse =
        await mediaPresignedUploadRequestPresignedUpload({
          file_name: selectedFile.name,
          content_type: selectedFile.type,
          file_size: selectedFile.size,
        });

      setProgress(30);

      // Step 2: Upload directly to S3 using presigned URL
      const uploadResponse = await fetch(presignedResponse.upload_url, {
        method: 'PUT',
        body: selectedFile,
        headers: {
          'Content-Type': selectedFile.type,
        },
      });

      if (!uploadResponse.ok) {
        throw new Error('Upload to S3 failed');
      }

      setUploadStatus('complete');
      setProgress(100);
      toast.success('File uploaded to S3 successfully');

      // Step 3: Call onSubmit with file_key and metadata
      // The consumer will handle registration and query invalidation
      console.log(`DEBUGGGIUNGGGG`, presignedResponse, uploadResponse);
      onSubmit({
        file_key: presignedResponse.file_key,
        file_name: selectedFile.name,
        file_size: selectedFile.size,
        mime_type: selectedFile.type,
      });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to upload media';
      setUploadStatus('error');
      setError(errorMessage);
      console.error('Upload error:', error);
      toast.error(errorMessage);
    }
  };

  const isProcessing = uploadStatus === 'uploading' || isSubmitting;
  const isComplete = uploadStatus === 'complete';

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {!selectedFile ? (
        <Dropzone
          onDrop={handleDrop}
          accept={{
            'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
            'video/*': ['.mp4', '.mov', '.avi', '.webm'],
          }}
          maxFiles={1}
          disabled={isProcessing}
        >
          <DropzoneEmptyState>
            <div className="flex flex-col items-center justify-center py-8">
              <div className="bg-muted text-muted-foreground flex size-12 items-center justify-center rounded-md">
                <UploadIcon size={24} />
              </div>
              <p className="my-2 text-lg font-medium">Upload media file</p>
              <p className="text-muted-foreground text-sm">
                Drag and drop or click to upload
              </p>
              <p className="text-muted-foreground mt-1 text-xs">
                Accepts images and videos
              </p>
            </div>
          </DropzoneEmptyState>
        </Dropzone>
      ) : (
        <div className="border-border rounded-lg border p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">
                {selectedFile.name}
              </p>
              <p className="text-muted-foreground text-xs">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>

            <div className="flex items-center gap-2">
              {uploadStatus === 'uploading' ? (
                <Loader2 className="text-primary h-4 w-4 animate-spin" />
              ) : uploadStatus === 'complete' ? (
                <CheckCircle2 className="h-4 w-4 text-green-600" />
              ) : uploadStatus === 'error' ? (
                <AlertCircle className="text-destructive h-4 w-4" />
              ) : null}

              {uploadStatus === 'idle' && (
                <Button
                  variant="ghost"
                  size="sm"
                  type="button"
                  onClick={removeFile}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>

          {previewUrl && (
            <div className="mt-4">
              <Image
                src={previewUrl}
                alt={selectedFile.name}
                className="max-h-64 w-full rounded-md object-contain"
              />
            </div>
          )}

          {uploadStatus === 'uploading' && (
            <div className="mt-3">
              <Progress value={progress} className="h-2" />
              <p className="text-muted-foreground mt-1 text-xs">
                Uploading to S3...
              </p>
            </div>
          )}

          {uploadStatus === 'error' && error && (
            <p className="text-destructive mt-2 text-xs">{error}</p>
          )}

          {uploadStatus === 'complete' && (
            <p className="mt-2 text-xs text-green-600">Upload complete!</p>
          )}
        </div>
      )}

      <div className="flex gap-3 pt-4">
        <Button
          type="submit"
          disabled={isProcessing || !selectedFile || isComplete}
          className="flex-1"
        >
          {uploadStatus === 'uploading'
            ? 'Uploading...'
            : isSubmitting
              ? 'Creating...'
              : isComplete
                ? 'Complete'
                : 'Upload & Create'}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isProcessing}
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </form>
  );
}
