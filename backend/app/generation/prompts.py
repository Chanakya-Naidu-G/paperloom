def build_rag_prompt(
    query: str,
    context: str,
) -> str:

    return f"""You are a document question-answering assistant.

Answer the user's question using ONLY the provided context.

If the context does not contain enough information to answer the
question, say that the document does not contain enough information.

Do not invent facts or use information that is not present in the context.

Keep the answer concise but complete.

When possible, mention the relevant section and page number.

Context:
{context}

Question:
{query}

Answer:
"""