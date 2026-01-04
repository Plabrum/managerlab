export type ViewMode = 'table' | 'gallery' | 'card' | 'list';

export interface ListViewConfig {
  [objectType: string]: ViewMode;
}
