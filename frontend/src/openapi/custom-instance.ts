import axios, { AxiosRequestConfig } from 'axios';

const instance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
  withCredentials: true,
});

export const customInstance = async <T>(
  config: AxiosRequestConfig
): Promise<T> => {
  try {
    const { data } = await instance(config);
    return data;
  } catch (error) {
    // Re-throw the error so it can be caught by React error boundaries
    throw error;
  }
};
