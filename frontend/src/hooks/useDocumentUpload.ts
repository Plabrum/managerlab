import { useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import {
  documentsPresignedUploadRequestPresignedUpload,
  useDocumentsRegisterRegisterDocument,
} from '@/openapi/documents/documents';

export type DocumentUploadStatus =
  | 'idle'
  | 'uploading'
  | 'registering'
  | 'complete'
  | 'error';

export interface DocumentUploadResult {
  documentId: string;
  fileKey: string;
}

export interface UseDocumentUploadReturn {
  uploadFile: (
    file: File,
    options?: {
      autoRegister?: boolean;
      onSuccess?: (result: DocumentUploadResult) => void;
    }
  ) => Promise<DocumentUploadResult | null>;
  status: DocumentUploadStatus;
  progress: number;
  error: string | null;
  reset: () => void;
}

/**
 * Hook for uploading document files to S3 and optionally registering them
 * Handles the full workflow: presigned URL → S3 upload → backend registration
 *
 * @example
 * ```tsx
 * const { uploadFile, status, progress } = useDocumentUpload();
 *
 * const handleUpload = async (file: File) => {
 *   const result = await uploadFile(file, {
 *     autoRegister: true,
 *     onSuccess: (result) => console.log('Uploaded:', result.documentId)
 *   });
 * };
 * ```
 */
export function useDocumentUpload(): UseDocumentUploadReturn {
  const [status, setStatus] = useState<DocumentUploadStatus>('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const registerDocumentMutation = useDocumentsRegisterRegisterDocument();

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
        onSuccess?: (result: DocumentUploadResult) => void;
      }
    ): Promise<DocumentUploadResult | null> => {
      const { autoRegister = true, onSuccess } = options || {};

      try {
        // Step 1: Request presigned URL from backend
        setStatus('uploading');
        setProgress(10);
        setError(null);

        const presignedResponse =
          await documentsPresignedUploadRequestPresignedUpload({
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

        let result: DocumentUploadResult;

        if (autoRegister) {
          // Step 3: Register the document in the database
          setStatus('registering');
          toast.success('File uploaded to S3');

          const registeredDocument = await registerDocumentMutation.mutateAsync(
            {
              data: {
                file_key: presignedResponse.file_key,
                file_name: file.name,
                file_size: file.size,
                mime_type: file.type,
              },
            }
          );

          result = {
            documentId: String(registeredDocument.id),
            fileKey: presignedResponse.file_key,
          };

          setProgress(100);
          setStatus('complete');
          toast.success('Document registered successfully');

          // Invalidate document list query to refresh
          await queryClient.invalidateQueries({
            queryKey: ['objects', 'documents'],
          });
        } else {
          // Just upload without registration
          result = {
            documentId: '', // No ID yet
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
          err instanceof Error ? err.message : 'Failed to upload document';
        setStatus('error');
        setError(errorMessage);
        console.error('Upload error:', err);
        toast.error(errorMessage);
        return null;
      }
    },
    [queryClient, registerDocumentMutation]
  );

  return {
    uploadFile,
    status,
    progress,
    error,
    reset,
  };
}
