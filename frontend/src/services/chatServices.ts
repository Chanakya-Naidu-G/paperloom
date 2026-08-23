const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

interface AskRequest {
  query: string;
  top_k?: number;
  document_ids?: string[];
}

interface AskSource {
  chunk_id: string;
  document_id: string;
  section: string;
  page_start: number;
  page_end: number;
}

interface AskResponse {
  query: string;
  answer: string;
  sources: AskSource[];
}

export async function askQuestion(
  query: string,
  topK: number = 5,
  documentIds?: string[],
): Promise<AskResponse> {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      top_k: topK,
      document_ids: documentIds,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `Ask request failed (${response.status}): ${errorText}`,
    );
  }

  return response.json();
}