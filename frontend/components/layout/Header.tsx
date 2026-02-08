"use client";

import { useSession, signOut } from "@/lib/auth-client";
import Link from "next/link";

export function Header() {
  const { data: session, isPending } = useSession();

  return (
    <header className="bg-white shadow">
      <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="text-xl font-bold text-gray-900">
          Todo App
        </Link>

        <div className="flex items-center gap-4">
          {isPending ? (
            <span className="text-gray-500">Loading...</span>
          ) : session ? (
            <>
              <Link
                href="/tasks"
                className="text-gray-600 hover:text-gray-900"
              >
                Tasks
              </Link>
              <Link
                href="/chat"
                className="text-gray-600 hover:text-gray-900"
              >
                Chat
              </Link>
              <span className="text-gray-600">{session.user.email}</span>
              <button
                onClick={() => signOut()}
                className="text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="text-gray-600 hover:text-gray-900"
              >
                Login
              </Link>
              <Link
                href="/register"
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
