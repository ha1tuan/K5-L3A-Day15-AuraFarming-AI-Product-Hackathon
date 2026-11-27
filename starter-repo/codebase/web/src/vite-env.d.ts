/// <reference types="vite/client" />
interface ImportMetaEnv { readonly VITE_API_URL?: string; readonly VITE_DEMO?: string }
interface ImportMeta { readonly env: ImportMetaEnv }
declare module '*.module.scss' { const classes: Record<string, string>; export default classes; }
