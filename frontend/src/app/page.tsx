import Link from "next/link";
import { ArrowRight, FileText } from "lucide-react";
import ThemeToggle from "@/components/workspace/ThemeToggle";

export default function HomePage() {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center bg-background px-4 py-8">
      <div className="absolute right-4 top-4">
        <ThemeToggle />
      </div>

      <div className="flex w-full max-w-md flex-col items-center rounded-2xl border border-border bg-surface p-8 text-center shadow-sm motion-safe:animate-in motion-safe:fade-in motion-safe:slide-in-from-bottom-2 motion-safe:duration-300 max-[767px]:p-6">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-sm">
          <FileText className="h-6 w-6" />
        </div>
        <h1 className="mt-4 text-2xl font-semibold tracking-tight text-foreground">
          PaperLoom
        </h1>
        <p className="text-sm font-medium text-muted-foreground">Research, organized</p>
        <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
          Your intelligent research companion. Upload PDFs, ask questions, and get grounded answers with citations — private and per-user isolated.
        </p>

        <Link
          href="/login"
          className="mt-6 inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-primary px-8 text-sm font-medium text-primary-foreground shadow-sm transition hover:bg-primary/90 motion-safe:transition-colors"
        >
          Open Research Workspace
          <ArrowRight className="h-4 w-4" />
        </Link>

        <p className="mt-6 text-xs text-faint">PDF only • 50 MB max • Secure by design</p>
      </div>

      <p className="mt-6 text-center text-xs text-faint">Secure • Per-user isolated • Grounded answers</p>
    </main>
  );
}