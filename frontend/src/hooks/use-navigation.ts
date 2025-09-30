'use client';

import { useRouter } from 'next/navigation';
import { useCallback } from 'react';

export function useNavigation(baseUrl = '') {
  const router = useRouter();

  const navigateToLink = useCallback(
    (link: string) => {
      const fullUrl = baseUrl ? `${baseUrl}/${link}` : `/${link}`;
      router.push(fullUrl);
    },
    [baseUrl, router]
  );

  return { navigateToLink };
}
