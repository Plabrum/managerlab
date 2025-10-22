import { useState, useCallback } from 'react';
import { toast } from 'sonner';
import {
  mediaPresignedUploadRequestPresignedUpload,
  useMediaRegisterRegisterMedia,
} from '@/openapi/media/media';
import { useQueryClient } from '@tanstack/react-query';

export type MediaUploadStatus =
  | 'idle'
  | 'uploading'
  | 'registering'
  | 'complete'
  | 'error';

export interface MediaUploadResult {
  mediaId: string;
  fileKey: string;
}

export interface UseMediaUploadReturn {
  uploadFile: (
    file: File,
    options?: {
      autoRegister?: boolean;
      onSuccess?: (result: MediaUploadResult) => void;
    }
  ) => Promise<MediaUploadResult | null>;
  status: MediaUploadStatus;
  progress: number;
  error: string | null;
  reset: () => void;
}

/**
 * Hook for uploading media files to S3 and optionally registering them
 * Handles the full workflow: presigned URL → S3 upload → backend registration
 *
 * @example
 * ```tsx
 * const { uploadFile, status, progress } = useMediaUpload();
 *
 * const handleUpload = async (file: File) => {
 *   const result = await uploadFile(file, {
 *     autoRegister: true,
 *     onSuccess: (result) => console.log('Uploaded:', result.mediaId)
 *   });
 * };
 * ```
 */
export function useMediaUpload(): UseMediaUploadReturn {
  const [status, setStatus] = useState<MediaUploadStatus>('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const registerMediaMutation = useMediaRegisterRegisterMedia();

  const reset = useCallback(() => {
    setStatus('idle');
    setProgress(0);
    setError(null);
  }, []);

  const uploadFile = useCallback(
    async (
      file: File,
      options?: {
        autoRegister?: boolean;
        onSuccess?: (result: MediaUploadResult) => void;
      }
    ): Promise<MediaUploadResult | null> => {
      const { autoRegister = true, onSuccess } = options || {};

      try {
        // Step 1: Request presigned URL from backend
        setStatus('uploading');
        setProgress(10);
        setError(null);

        const presignedResponse =
          await mediaPresignedUploadRequestPresignedUpload({
            file_name: file.name,
            content_type: file.type,
            file_size: file.size,
          });

        setProgress(30);

        // Step 2: Upload directly to S3 using presigned URL
        const uploadResponse = await fetch(presignedResponse.upload_url, {
          method: 'PUT',
          body: file,
          headers: {
            'Content-Type': file.type,
          },
        });

        if (!uploadResponse.ok) {
          throw new Error('Upload to S3 failed');
        }

        setProgress(60);

        let result: MediaUploadResult;

        if (autoRegister) {
          // Step 3: Register the media in the database
          setStatus('registering');
          toast.success('File uploaded to S3');

          const registeredMedia = await registerMediaMutation.mutateAsync({
            data: {
              file_key: presignedResponse.file_key,
              file_name: file.name,
              file_size: file.size,
              mime_type: file.type,
            },
          });

          result = {
            mediaId: String(registeredMedia.id),
            fileKey: presignedResponse.file_key,
          };

          setProgress(100);
          setStatus('complete');
          toast.success('Media registered successfully');

          // Invalidate media list query to refresh
          await queryClient.invalidateQueries({
            queryKey: ['objects', 'media'],
          });
        } else {
          // Just upload without registration
          result = {
            mediaId: '', // No ID yet
            fileKey: presignedResponse.file_key,
          };

          setProgress(100);
          setStatus('complete');
          toast.success('File uploaded to S3 successfully');
        }

        // Call success callback if provided
        if (onSuccess) {
          onSuccess(result);
        }

        return result;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to upload media';
        setStatus('error');
        setError(errorMessage);
        console.error('Upload error:', err);
        toast.error(errorMessage);
        return null;
      }
    },
    [queryClient, registerMediaMutation]
  );

  return {
    uploadFile,
    status,
    progress,
    error,
    reset,
  };
}
