import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <Link
        href="/workspace"
        className="rounded-lg border px-6 py-3"
      >
        Open Research Workspace
      </Link>
    </main>
  );
}