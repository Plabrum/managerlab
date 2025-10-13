import { instance } from './custom-instance';

// Add interceptor to handle server-side cookie forwarding during SSR
instance.interceptors.request.use(async (requestConfig) => {
  // Only run on server (during SSR/RSC)
  if (typeof window === 'undefined') {
    try {
      // Dynamically import next/headers (only available on server)
      const { cookies } = await import('next/headers');
      const cookieStore = await cookies();
      const session = cookieStore.get('session')?.value;

      // Forward session cookie to backend
      if (session) {
        requestConfig.headers.Cookie = `session=${session}`;
      }
    } catch {
      // Ignore if cookies() is not available or fails
      // This can happen in edge cases or older Next.js versions
    }
  }

  return requestConfig;
});
