export interface Document {
  id: string;
  name: string;
  type: 'pdf' | 'text' | 'markdown';
  content: string;
  size: number;
  uploadedAt: Date;
  updatedAt: Date;
}

export interface DocumentMetadata {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadedAt: Date;
}
