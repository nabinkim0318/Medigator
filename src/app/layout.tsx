import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import ResearchPrototypeBanner from "./components/ResearchPrototypeBanner";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Medigator",
  description:
    "Research prototype. Synthetic/demo data only. Not for diagnosis, treatment, clinical use, or production. Does not claim HIPAA compliance.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning={true}
      >
        <ResearchPrototypeBanner />
        {children}
      </body>
    </html>
  );
}
