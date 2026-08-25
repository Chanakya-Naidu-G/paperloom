import {
  API_BASE_URL,
  extractErrorMessage,
  getAuthHeaders,
} from '@/lib/api';

export interface UploadResponse {
  success: boolean;
  message: string;
  document_id?: string;
  original_filename?: string;
  pages?: number;
  characters?: number;
  chunk_count?: number;
}

export interface DocumentListItem {
  document_id: string;
  original_filename: string;
  file_size: number;
  page_count: number;
  character_count: number;
  chunk_count: number;
  status: string;
  uploaded_at: string;
}

export async function uploadDocument(
  file: File,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!response.ok) {
    throw new Error(
      await extractErrorMessage(response, 'Failed to upload document.'),
    );
  }

  return response.json();
}

export async function fetchDocuments(): Promise<DocumentListItem[]> {
  const response = await fetch(`${API_BASE_URL}/documents`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(
      await extractErrorMessage(response, 'Failed to load your documents.'),
    );
  }

  return response.json();
}
