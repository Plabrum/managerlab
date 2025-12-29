import { useCallback } from 'react';
import { useNavigate } from '@tanstack/react-router';

export function useNavigation(baseUrl = '') {
  const navigate = useNavigate();

  const navigateToLink = useCallback(
    (link: string) => {
      const fullUrl = baseUrl ? `${baseUrl}/${link}` : `/${link}`;
      navigate({ to: fullUrl });
    },
    [baseUrl, navigate]
  );

  return { navigateToLink };
}
