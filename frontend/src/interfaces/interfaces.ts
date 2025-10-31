export interface Tag {
  id: number;
  name: string;
}

export interface Asset {
  id: number;
  folder_path: string;
  format: string;
  file_size: number;
  width: string;
  height: string;
  created_at: number;
  updated_at: number;
  name: string;
  system_name: string;
  is_private: boolean;
  is_favorite: boolean;
  tags: Tag[];
  file_url: string;
  path: string;
}
export interface Filter {
  keyword?: string;
  match_type?: string;
  start_date?: string;
  end_date?: string;
  file_extension?: string;
  is_favorite?: boolean;
  is_deleted?: boolean;
  is_private?: boolean;
  is_image?: boolean;
  shape?: string;
  tag?: string;
  folder_path?: string;
  sort_by?: string;
  sort_order?: string;
}
export interface Folder {
  id: number;
  project_id?: number;
  parent_id?: number;
  name?: string;
  slug?: string;
  path: string;
  created_at?: Date;
  is_default?: boolean;
  length: number;
  children?: Folder[];
}
export interface Project {
  id: number;
  name: string;
  slug?: string;
  api_key: string;
  api_secret: string;
  description: string;
  created_at?: string;
}
export interface ErrorMessage {
  message: string;
}
