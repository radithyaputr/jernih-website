"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import Image from "next/image"
import {
  Brain,
  LayoutDashboard,
  Share2,
  ClipboardList,
  ShieldCheck,
  Search,
  FileText,
  BarChart3,
  Globe,
  Menu,
  X,
  Sun,
  Moon,
} from "lucide-react"
import { useState, useEffect } from "react"
import { useTheme } from "next-themes"
import { motion, AnimatePresence } from "framer-motion"

const navItems = [
  { href: "/copilot", label: "AI Civic Copilot", icon: Brain },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/knowledge-graph", label: "Knowledge Graph", icon: Share2 },
  { href: "/action-plan", label: "Action Plan", icon: ClipboardList },
  { href: "/hoax-checker", label: "Hoax Checker", icon: Search },
  { href: "/procedure-simplifier", label: "Simplifier", icon: FileText },
  { href: "/policy-simulator", label: "Policy Simulator", icon: BarChart3 },
  { href: "/community-health", label: "Community Health", icon: Globe },
  { href: "/responsible-ai", label: "Responsible AI", icon: ShieldCheck },
]

export function Navbar() {
  const pathname = usePathname()
  const [mobileOpen, setMobileOpen] = useState(false)
  const { theme, resolvedTheme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => setMounted(true), [])

  const toggleTheme = () => {
    if (theme === "dark") setTheme("light")
    else if (theme === "light") setTheme("dark")
    else setTheme("dark")
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass border-b">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2.5">
              <Image src="/jernih-logo.svg" alt="JERNIH" width={30} height={30} className="shrink-0" />
              <span className="font-bold text-lg tracking-tight">
                JERNIH
              </span>
            </Link>
            <nav className="hidden lg:flex items-center gap-1">
              {navItems.slice(0, 5).map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                return (
                  <Link key={item.href} href={item.href}>
                    <span
                      className={cn(
                        "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200",
                        isActive
                          ? "bg-primary/10 text-primary"
                          : "text-muted-foreground hover:text-foreground hover:bg-accent"
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      {item.label}
                    </span>
                  </Link>
                )
              })}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="brand" size="sm" className="hidden sm:flex">
              <Brain className="h-4 w-4 mr-1.5" />
              Tanya JERNIH
            </Button>
            <button
              onClick={toggleTheme}
              className="p-2 hover:bg-accent rounded-lg transition-colors"
              aria-label="Toggle dark mode"
            >
              {mounted && resolvedTheme === "dark" ? (
                <Sun className="h-5 w-5" />
              ) : (
                <Moon className="h-5 w-5" />
              )}
            </button>
            <button
              className="lg:hidden p-2 hover:bg-accent rounded-lg transition-colors"
              onClick={() => setMobileOpen(!mobileOpen)}
            >
              {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="border-t bg-background/95 backdrop-blur-lg lg:hidden overflow-hidden"
          >
            <nav className="px-4 py-3 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                return (
                  <Link key={item.href} href={item.href} onClick={() => setMobileOpen(false)}>
                    <span
                      className={cn(
                        "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                        isActive
                          ? "bg-primary/10 text-primary"
                          : "text-muted-foreground hover:text-foreground hover:bg-accent"
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      {item.label}
                    </span>
                  </Link>
                )
              })}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
