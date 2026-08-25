import { AskRequest, AskResponse } from '@/types/chat';
import {
  API_BASE_URL,
  extractErrorMessage,
  getAuthHeaders,
} from '@/lib/api';

export async function askQuestion(
  request: AskRequest,
): Promise<AskResponse> {
  const response = await fetch(`${API_BASE_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(
      await extractErrorMessage(
        response,
        'Failed to get an answer. Please try again.',
      ),
    );
  }

  return response.json();
}
