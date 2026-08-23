export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Citation {
  id: string;
  source: string;
  page?: number;
  text?: string;
}

export interface AskRequest {
  query: string;
  top_k?: number;
  document_ids?: string[];
}

export interface AskSource {
  chunk_id: string;
  document_id: string;
  section: string;
  page_start: number;
  page_end: number;
}

export interface AskResponse {
  query: string;
  answer: string;
  sources: AskSource[];
}
