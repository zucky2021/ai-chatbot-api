interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  /** S3 Asset Base URL */
  readonly VITE_ASSET_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
