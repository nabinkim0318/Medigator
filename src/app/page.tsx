import { FloatingCedarChat } from "@/cedar/components/chatComponents/FloatingCedarChat";

export default function Home() {
  return (
    <div className="h-screen">
      {/* This automatically works */}
      <FloatingCedarChat />
    </div>
  );
}
