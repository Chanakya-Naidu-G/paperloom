interface ConversationHeaderProps {
  title: string;
  messageCount: number;
}

export function ConversationHeader({
  title,
  messageCount,
}: ConversationHeaderProps) {
  return (
    <div className="border-b border-border px-6 py-4">
      <h2 className="text-base font-semibold text-foreground">
        {title}
      </h2>

      <p className="mt-0.5 text-[11px] text-muted-foreground">
        {messageCount} messages
      </p>
    </div>
  );
}
