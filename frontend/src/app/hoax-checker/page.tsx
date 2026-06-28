"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { generateMockHoaxCheck } from "@/lib/mock-data"
import { api } from "@/lib/api"
import type { HoaxCheckResponse } from "@/lib/api"
import {
  Search,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Copy,
} from "lucide-react"

export default function HoaxCheckerPage() {
  const [input, setInput] = useState("")
  const [result, setResult] = useState<HoaxCheckResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [mode, setMode] = useState<"text" | "url" | "news">("text")

  const handleCheck = async () => {
    if (!input.trim() || isLoading) return
    setIsLoading(true)
    try {
      const res = await api.hoaxChecker.check({ text: input, type: mode })
      setResult(res)
    } catch {
      // Fallback to mock data if API is unavailable
      setResult(generateMockHoaxCheck())
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 py-8 space-y-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <h1 className="text-2xl font-bold">AI Hoax Checker</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Verifikasi informasi dan deteksi hoaks dengan analisis dari sumber terpercaya
          </p>
        </div>

        <Card>
          <CardContent className="p-6">
            <div className="flex gap-2 mb-4">
              {[
                { key: "text" as const, label: "Teks" },
                { key: "url" as const, label: "URL" },
                { key: "news" as const, label: "Berita" },
              ].map((m) => (
                <Button
                  key={m.key}
                  variant={mode === m.key ? "brand" : "outline"}
                  size="sm"
                  onClick={() => setMode(m.key)}
                >
                  {m.label}
                </Button>
              ))}
            </div>

            <div className="space-y-2">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={
                  mode === "text"
                    ? "Masukkan teks informasi yang ingin diverifikasi..."
                    : mode === "url"
                    ? "Masukkan URL berita atau informasi..."
                    : "Tempelkan judul/konten berita..."
                }
                rows={5}
                className="w-full rounded-xl border border-input bg-background px-4 py-3 text-sm resize-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-all"
              />
              <Button
                onClick={handleCheck}
                disabled={!input.trim() || isLoading}
                variant="brand"
                className="w-full"
                size="lg"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin mr-2" />
                ) : (
                  <Search className="h-5 w-5 mr-2" />
                )}
                Verifikasi Informasi
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Verdict */}
          <Card className={`border-2 ${
            result.verdict === "hoax" ? "border-destructive/30" : result.verdict === "questionable" ? "border-warning/30" : "border-success/30"
          }`}>
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-full ${
                  result.verdict === "hoax" ? "bg-destructive/10" : result.verdict === "questionable" ? "bg-warning/10" : "bg-success/10"
                }`}>
                  {result.verdict === "hoax" ? (
                    <AlertTriangle className="h-8 w-8 text-destructive" />
                  ) : result.verdict === "questionable" ? (
                    <AlertTriangle className="h-8 w-8 text-warning" />
                  ) : (
                    <CheckCircle2 className="h-8 w-8 text-success" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-bold capitalize">
                      {result.verdict === "hoax" ? "HOAKS" : result.verdict === "questionable" ? "Mencurigakan" : "Kredibel"}
                    </h3>
                    <Badge variant={result.verdict === "hoax" ? "destructive" : result.verdict === "questionable" ? "warning" : "success"}>
                      Skor: {result.credibility_score}/100
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">{result.analysis}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Fact Checks */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-primary" />
                Hasil Fact Check
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {result.fact_checks.map((fc) => (
                <div key={fc.claim} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div className="flex-1">
                    <div className="text-sm font-medium">{fc.claim}</div>
                    <div className="text-xs text-muted-foreground">Sumber: {fc.source}</div>
                  </div>
                  <Badge variant={fc.verdict.includes("SALAH") ? "destructive" : "success"} className="ml-3 shrink-0">
                    {fc.verdict}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Source Comparison */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Copy className="h-5 w-5 text-primary" />
                Perbandingan Sumber
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {result.source_comparison.map((src) => (
                <div key={src.source} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                  <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                    src.alignment === "supports" ? "bg-destructive" : src.alignment === "contradicts" ? "bg-success" : "bg-muted-foreground"
                  }`} />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">{src.source}</span>
                      <Badge variant={src.alignment === "supports" ? "destructive" : src.alignment === "contradicts" ? "success" : "secondary"} className="text-xs">
                        {src.alignment === "supports" ? "Mendukung" : src.alignment === "contradicts" ? "Bertentangan" : "Netral"}
                      </Badge>
                    </div>
                    {src.excerpt && (
                      <p className="text-xs text-muted-foreground mt-1 italic">&ldquo;{src.excerpt}&rdquo;</p>
                    )}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Indicators */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-warning" />
                Indikator Informasi Mencurigakan
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {result.indicators.map((indicator) => (
                  <li key={indicator} className="flex items-start gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-warning mt-0.5 shrink-0" />
                    <span>{indicator}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}
