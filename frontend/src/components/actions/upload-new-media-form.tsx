import {
  Loader2,
  UploadIcon,
  CheckCircle2,
  AlertCircle,
  X,
} from 'lucide-react';
import { useState, useCallback, useEffect } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Dropzone, DropzoneEmptyState } from '@/components/ui/dropzone';
import { Image } from '@/components/ui/image';
import { Progress } from '@/components/ui/progress';
import { useMediaUpload } from '@/hooks/useMediaUpload';
import { AddMediaToDeliverableSchema } from '@/openapi/ariveAPI.schemas';

interface UploadNewMediaFormProps {
  onSubmit: (data: AddMediaToDeliverableSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

/**
 * Form for uploading new media and adding it to a deliverable
 * Handles file selection, upload, registration, and calls onSubmit when complete
 */
export function UploadNewMediaForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: UploadNewMediaFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // Use upload hook with callback on success
  const {
    uploadFile,
    status: uploadStatus,
    progress,
    error,
    reset,
  } = useMediaUpload();

  const handleDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (file) {
        setSelectedFile(file);
        reset();

        // Create preview URL for images
        if (file.type.startsWith('image/')) {
          const url = URL.createObjectURL(file);
          setPreviewUrl(url);
        } else {
          setPreviewUrl(null);
        }
      }
    },
    [reset]
  );

  const removeFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    reset();
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

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file');
      return;
    }

    // Upload with auto-registration and call onSubmit directly on success
    await uploadFile(selectedFile, {
      autoRegister: true,
      onSuccess: (result) => {
        // Call onSubmit directly - no useEffect needed!
        onSubmit({ media_ids: [result.mediaId] });
      },
    });
  };

  const isProcessing =
    uploadStatus === 'uploading' ||
    uploadStatus === 'registering' ||
    isSubmitting;

  return (
    <div className="space-y-4">
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
              {uploadStatus === 'uploading' ||
              uploadStatus === 'registering' ? (
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

          {(uploadStatus === 'uploading' || uploadStatus === 'registering') && (
            <div className="mt-3">
              <Progress value={progress} className="h-2" />
              <p className="text-muted-foreground mt-1 text-xs">
                {uploadStatus === 'uploading'
                  ? 'Uploading to S3...'
                  : 'Registering media...'}
              </p>
            </div>
          )}

          {uploadStatus === 'error' && error && (
            <p className="text-destructive mt-2 text-xs">{error}</p>
          )}

          {uploadStatus === 'complete' && (
            <p className="mt-2 text-xs text-green-600">
              Upload complete! Adding to deliverable...
            </p>
          )}
        </div>
      )}

      <div className="flex gap-3 pt-4">
        <Button
          type="button"
          onClick={handleUpload}
          disabled={isProcessing || !selectedFile}
          className="flex-1"
        >
          {isProcessing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {uploadStatus === 'uploading'
                ? 'Uploading...'
                : uploadStatus === 'registering'
                  ? 'Registering...'
                  : 'Adding...'}
            </>
          ) : (
            'Upload & Add Media'
          )}
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
    </div>
  );
}
