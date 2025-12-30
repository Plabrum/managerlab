/**
 * Cookie utility functions for managing browser cookies
 */

export interface CookieOptions {
  path?: string;
  maxAge?: number;
  expires?: Date;
  secure?: boolean;
  sameSite?: 'Strict' | 'Lax' | 'None';
}

/**
 * Get a cookie value by name
 * @param name - Cookie name
 * @returns Cookie value or null if not found
 */
export function getCookie(name: string): string | null {
  const cookies = document.cookie.split('; ');
  const cookie = cookies.find((c) => c.startsWith(`${name}=`));
  return cookie ? cookie.split('=')[1] : null;
}

/**
 * Check if a cookie exists
 * @param name - Cookie name
 * @returns True if cookie exists
 */
export function hasCookie(name: string): boolean {
  return document.cookie.includes(`${name}=`);
}

/**
 * Set a cookie with optional parameters
 * @param name - Cookie name
 * @param value - Cookie value
 * @param options - Cookie options (path, maxAge, expires, secure, sameSite)
 */
export function setCookie(
  name: string,
  value: string,
  options: CookieOptions = {}
): void {
  const {
    path = '/',
    maxAge,
    expires,
    secure = window.location.protocol === 'https:',
    sameSite = 'Lax',
  } = options;

  let cookieString = `${name}=${value}; path=${path}`;

  if (maxAge !== undefined) {
    cookieString += `; max-age=${maxAge}`;
  }

  if (expires) {
    cookieString += `; expires=${expires.toUTCString()}`;
  }

  if (secure) {
    cookieString += '; Secure';
  }

  cookieString += `; SameSite=${sameSite}`;

  document.cookie = cookieString;
}

/**
 * Delete a cookie by setting its expiration to the past
 * @param name - Cookie name
 * @param path - Cookie path (default: '/')
 */
export function deleteCookie(name: string, path: string = '/'): void {
  setCookie(name, '', {
    path,
    expires: new Date(0), // Thu, 01 Jan 1970 00:00:00 UTC
  });
}
