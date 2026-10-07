import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Autonomous Satellite Power & Propulsion Dashboard",
  description: "Interactive Real-Time Dashboard for LEO Satellite Station-Keeping & EPS Energy Balance",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-space-900 text-gray-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
