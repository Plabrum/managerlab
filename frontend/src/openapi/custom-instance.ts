import axios, { AxiosRequestConfig } from 'axios';

const instance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
  withCredentials: true,
});

export const customInstance = async <T>(
  config: AxiosRequestConfig
): Promise<T> => {
  const { data } = await instance(config);
  return data;
};
