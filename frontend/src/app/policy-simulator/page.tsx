"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { generateMockPolicySimulation } from "@/lib/mock-data"
import { api } from "@/lib/api"
import type { PolicySimulationResponse } from "@/lib/api"
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Minus,
  Users,
  AlertTriangle,
  Lightbulb,
  Loader2,
  Sparkles,
} from "lucide-react"
import { formatNumber } from "@/lib/utils"
import { Input } from "@/components/ui/input"

export default function PolicySimulatorPage() {
  const [policy, setPolicy] = useState("")
  const [change, setChange] = useState("")
  const [result, setResult] = useState<PolicySimulationResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSimulate = async () => {
    if (!policy.trim() || !change.trim() || isLoading) return
    setIsLoading(true)
    try {
      const res = await api.policySimulator.simulate({ policy, change })
      setResult(res)
    } catch {
      // Fallback to mock data if API is unavailable
      setResult(generateMockPolicySimulation(policy, change))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 py-8 space-y-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold">AI Policy Impact Simulator</h1>
          </div>
          <p className="text-muted-foreground text-sm">
            Simulasikan dampak perubahan kebijakan terhadap jutaan warga Indonesia
          </p>
        </div>

        <Card>
          <CardContent className="p-6 space-y-4">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Kebijakan</label>
              <Input
                value={policy}
                onChange={(e) => setPolicy(e.target.value)}
                placeholder="Contoh: Program Indonesia Pintar (PIP)"
                className="h-11"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Perubahan yang Disimulasikan</label>
              <Input
                value={change}
                onChange={(e) => setChange(e.target.value)}
                placeholder="Contoh: Perubahan batas penghasilan orang tua dari Rp500rb menjadi Rp1jt"
                className="h-11"
              />
            </div>
            <Button
              onClick={handleSimulate}
              disabled={!policy.trim() || !change.trim() || isLoading}
              variant="brand"
              size="lg"
              className="w-full"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin mr-2" />
              ) : (
                <BarChart3 className="h-5 w-5 mr-2" />
              )}
              Simulasikan Dampak Kebijakan
            </Button>
          </CardContent>
        </Card>
      </motion.div>

      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Summary */}
          <Card className="gradient-brand text-white">
            <CardContent className="p-6">
              <p className="text-lg font-medium leading-relaxed">{result.summary}</p>
            </CardContent>
          </Card>

          {/* Coverage Change */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-primary" />
                Perubahan Cakupan Penerima
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center gap-8 py-4">
                <div className="text-center">
                  <div className="text-sm text-muted-foreground mb-1">Sebelum</div>
                  <div className="text-3xl font-bold">{formatNumber(result.coverage_change.before)}</div>
                </div>
                <ArrowRightUp className="h-8 w-8 text-success" />
                <div className="text-center">
                  <div className="text-sm text-muted-foreground mb-1">Sesudah</div>
                  <div className="text-3xl font-bold">{formatNumber(result.coverage_change.after)}</div>
                </div>
                <div className="text-center p-3 rounded-lg bg-success/10">
                  <div className="text-sm text-muted-foreground mb-1">Perubahan</div>
                  <div className="text-2xl font-bold text-success">+{formatNumber(result.coverage_change.difference)}</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Affected Groups */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-primary" />
                Kelompok Terdampak
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {result.affected_groups.map((group) => (
                <div key={group.group} className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
                  <div className="flex items-center gap-3">
                    {group.impact === "positive" ? (
                      <TrendingUp className="h-5 w-5 text-success" />
                    ) : group.impact === "negative" ? (
                      <TrendingDown className="h-5 w-5 text-destructive" />
                    ) : (
                      <Minus className="h-5 w-5 text-muted-foreground" />
                    )}
                    <div>
                      <div className="text-sm font-medium">{group.group}</div>
                      <div className="text-xs text-muted-foreground">{group.estimate}</div>
                    </div>
                  </div>
                  <Badge variant={group.impact === "positive" ? "success" : group.impact === "negative" ? "destructive" : "secondary"}>
                    {group.impact === "positive" ? "Positif" : group.impact === "negative" ? "Negatif" : "Netral"}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Opportunity Loss & Social Impact */}
          <div className="grid sm:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-warning" />
                  Potensi Kehilangan Akses
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground leading-relaxed">{result.opportunity_loss}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Dampak Sosial
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground leading-relaxed">{result.social_impact}</p>
              </CardContent>
            </Card>
          </div>

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-primary" />
                Rekomendasi Kebijakan
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {result.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                    <div className="w-6 h-6 rounded-full gradient-brand text-white text-xs font-bold flex items-center justify-center shrink-0">
                      {i + 1}
                    </div>
                    <span className="text-sm pt-0.5">{rec}</span>
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

function ArrowRightUp({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M7 17L17 7" />
      <path d="M7 7h10v10" />
    </svg>
  )
}
