import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ArbStream - Arbitrage Betting Dashboard",
  description: "Find and exploit arbitrage betting opportunities in real-time",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
