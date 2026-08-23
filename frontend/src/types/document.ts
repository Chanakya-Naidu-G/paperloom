export interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'text' | 'markdown';
  size: number;
  uploadedAt: Date;
  updatedAt: Date;
  pages?: number;
  characters?: number;
  chunkCount?: number;
}

export interface DocumentMetadata {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadedAt: Date;
  pages?: number;
  chunkCount?: number;
}