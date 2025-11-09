import type { AppRouterInstance } from 'next/dist/shared/lib/app-router-context.shared-runtime';
import type { ActionExecutionResponse } from '@/openapi/ariveAPI.schemas';

/**
 * Handle action result based on response metadata
 * Supports redirects (including parent navigation) and file downloads
 */
export function handleActionResult(
  response: ActionExecutionResponse,
  router: AppRouterInstance
): void {
  if (!response.action_result) {
    return;
  }

  // Type narrowing based on which fields are present
  if ('path' in response.action_result) {
    // RedirectActionResult
    const path = (response.action_result as { path: string }).path;
    if (path === '..') {
      // Navigate to parent (for delete actions)
      const currentPath = window.location.pathname;
      const parentPath = currentPath.substring(0, currentPath.lastIndexOf('/'));
      if (parentPath) {
        router.push(parentPath);
      }
    } else {
      // Navigate to specific path (for create actions)
      router.push(path);
    }
  } else if (
    'url' in response.action_result &&
    'filename' in response.action_result
  ) {
    // DownloadFileActionResult - trigger browser download
    const { url, filename } = response.action_result as {
      url: string;
      filename: string;
    };
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}
