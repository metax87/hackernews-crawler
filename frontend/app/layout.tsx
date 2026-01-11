import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HN AI Stories",
  description: "Hacker News AI 相关故事展示",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
