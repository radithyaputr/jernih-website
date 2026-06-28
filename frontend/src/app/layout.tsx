import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Navbar } from "@/components/navbar"
import { Providers } from "./providers"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "JERNIH — AI Civic Operating System",
  description: "Indonesia's AI Civic Operating System. Informasi yang terang, bukan yang bising.",
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="id" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <Navbar />
          <main className="pt-16 min-h-screen">{children}</main>
        </Providers>
      </body>
    </html>
  )
}
