import axios, { AxiosRequestConfig } from 'axios';
import { config } from '@/lib/config';

const instance = axios.create({
  baseURL: config.api.baseUrl,
  withCredentials: true,
});

export const customInstance = async <T>(
  config: AxiosRequestConfig
): Promise<T> => {
  const { data } = await instance(config);
  return data;
};
