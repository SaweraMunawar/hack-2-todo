import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { Header } from "@/components/layout/Header";
import { ChatLayout } from "@/components/chat/ChatLayout";

export default async function ChatPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/login");
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />
      <ChatLayout />
    </div>
  );
}
