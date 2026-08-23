import { AskRequest, AskResponse } from '@/types/chat';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function askQuestion(
  request: AskRequest,
): Promise<AskResponse> {
  const response = await fetch(`${API_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || 'Failed to get answer.');
  }

  return response.json();
}
