declare module '*.css';
declare module '*.woff2?url' {
  const url: string;
  export default url;
}

interface ImportMetaEnv {
  readonly SSG_MD: boolean;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
