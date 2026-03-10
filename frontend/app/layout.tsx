import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Clever AI Tutor",
  description: "Next.js + FastAPI with shared main-site authentication.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
