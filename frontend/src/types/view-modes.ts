export type ViewMode = 'table' | 'gallery' | 'card';

export interface ListViewConfig {
  [objectType: string]: ViewMode;
}
