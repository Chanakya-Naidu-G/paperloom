const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export interface UploadResponse {
  success: boolean;
  message: string;
  original_filename?: string;
  stored_filename?: string;
  path?: string;
  pages?: number;
  characters?: number;
  chunk_count?: number;
}

export async function uploadDocument(
  file: File,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Upload failed (${response.status}): ${errorText}`,
    );
  }

  return response.json();
}