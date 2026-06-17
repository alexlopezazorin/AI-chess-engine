import type { Metadata } from "next";
import {Fruktur} from "next/font/google";
import "./globals.css";

const fruktur = Fruktur({
  weight: "400"
})


export const metadata: Metadata = {
  title: "Chess Engine",
  description: "A chess engine built with Next.js and Python.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={fruktur.className}>{children}</body>
    </html>
  );
}
