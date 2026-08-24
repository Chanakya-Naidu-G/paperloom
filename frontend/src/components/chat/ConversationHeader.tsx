interface ConversationHeaderProps {
  title: string;
  messageCount: number;
}

export function ConversationHeader({
  title,
  messageCount,
}: ConversationHeaderProps) {
  return (
    <div className="border-b border-border px-6 py-4 max-[1023px]:px-4 max-[767px]:px-3">
      <h2 className="truncate text-base font-semibold text-foreground">
        {title}
      </h2>

      <p className="mt-0.5 text-[11px] text-muted-foreground">
        {messageCount} messages
      </p>
    </div>
  );
}
