import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  useDashboardsListDashboardsSuspense,
  useDashboardsIdUpdateDashboard,
} from '@/openapi/dashboards/dashboards';
import type { ObjectTypes } from '@/openapi/ariveAPI.schemas';
import type { ViewMode, ListViewConfig } from '@/types/view-modes';

export function useViewModePreference(objectType: ObjectTypes) {
  const { data: dashboards } = useDashboardsListDashboardsSuspense();
  const updateDashboard = useDashboardsIdUpdateDashboard();

  // Find personal dashboard (user_id is set, is_personal is true)
  const personalDashboard = dashboards?.find((d) => d.is_personal);

  // Extract current view mode from config
  const savedMode =
    (personalDashboard?.config?.list_views as ListViewConfig)?.[objectType] ||
    ('table' as ViewMode);

  const [viewMode, setViewModeState] = useState<ViewMode>(savedMode);

  // Sync local state when dashboard data changes
  useEffect(() => {
    setViewModeState(savedMode);
  }, [savedMode]);

  // Debounced setter that persists to backend
  useEffect(() => {
    // Don't sync if mode hasn't changed from saved value
    if (viewMode === savedMode) {
      return;
    }

    // Debounce the API call
    const timeoutId = setTimeout(() => {
      if (!personalDashboard) {
        toast.error('Unable to save view preference');
        return;
      }

      const updatedConfig = {
        ...personalDashboard.config,
        list_views: {
          ...(personalDashboard.config?.list_views || {}),
          [objectType]: viewMode,
        },
      };

      updateDashboard.mutate(
        {
          id: personalDashboard.id,
          data: {
            name: personalDashboard.name,
            config: updatedConfig,
            is_default: personalDashboard.is_default,
          },
        },
        {
          onError: (error) => {
            const errorMessage =
              error && typeof error === 'object' && 'message' in error
                ? String(error.message)
                : 'Unknown error';
            toast.error(`Failed to save view preference: ${errorMessage}`);
            // Revert to saved mode on error
            setViewModeState(savedMode);
          },
        }
      );
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [viewMode, savedMode, personalDashboard, objectType, updateDashboard]);

  return {
    viewMode,
    setViewMode: setViewModeState,
    isLoading: updateDashboard.isPending,
  };
}
