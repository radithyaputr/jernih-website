"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { generateMockActionPlan } from "@/lib/mock-data"
import { api } from "@/lib/api"
import type { ActionPlanResponse } from "@/lib/api"
import {
  ClipboardList,
  Send,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Lightbulb,
  FileText,
  TrendingUp,
  Loader2,
  ChevronRight,
  ShieldCheck,
} from "lucide-react"

const examples = [
  "Saya ingin mendaftar kuliah tapi tidak punya biaya",
  "Orang tua saya pensiunan PNS",
  "Saya korban PHK",
  "Saya ingin memulai usaha kecil",
]

export default function ActionPlanPage() {
  const [input, setInput] = useState("")
  const [plan, setPlan] = useState<ActionPlanResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleGenerate = async () => {
    if (!input.trim() || isLoading) return
    setIsLoading(true)
    try {
      const result = await api.actionPlan.generate({ situation: input })
      setPlan(result)
    } catch {
      // Fallback to mock data if API is unavailable
      setPlan(generateMockActionPlan(input))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 py-8 space-y-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <h1 className="text-2xl font-bold">AI Action Plan Generator</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Ceritakan situasi Anda, dan AI akan menyusun rencana aksi personal lengkap dengan timeline dan dokumen
          </p>
        </div>

        {/* Input */}
        <div className="glass rounded-xl p-6 border mb-8">
          <label className="text-sm font-medium mb-2 block">Deskripsikan situasi Anda</label>
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Contoh: Ayah saya meninggal, saya perlu mengurus dokumen..."
              className="rounded-xl h-12 px-4 text-sm"
              onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
            />
            <Button
              onClick={handleGenerate}
              disabled={!input.trim() || isLoading}
              variant="brand"
              size="xl"
              className="shrink-0"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <>
                  Generate Plan
                  <Send className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          </div>
          <div className="flex flex-wrap gap-2 mt-3">
            {examples.map((ex) => (
              <button
                key={ex}
                onClick={() => { setInput(ex) }}
                className="text-xs px-3 py-1.5 rounded-full border bg-card hover:bg-accent transition-all text-muted-foreground hover:text-foreground"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {plan && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Title & Score */}
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold">{plan.title}</h2>
              <p className="text-sm text-muted-foreground mt-1">{plan.overview}</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-gradient">{plan.citizen_success_score}</div>
              <div className="text-xs text-muted-foreground">Citizen Success Score</div>
            </div>
          </div>

          {/* Score Cards */}
          <div className="grid grid-cols-3 gap-4">
            {[
              { label: "Document Readiness", score: plan.document_readiness, icon: FileText },
              { label: "Eligibility Score", score: plan.eligibility_score, icon: ShieldCheck },
              { label: "Program Match", score: plan.program_match, icon: TrendingUp },
            ].map((item) => {
              const Icon = item.icon
              return (
                <Card key={item.label}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Icon className="h-4 w-4 text-primary" />
                      <span className="text-xs text-muted-foreground">{item.label}</span>
                    </div>
                    <div className="flex items-end gap-1">
                      <span className="text-2xl font-bold">{item.score}</span>
                      <span className="text-sm text-muted-foreground mb-1">/100</span>
                    </div>
                    <div className="h-1.5 bg-muted rounded-full mt-2 overflow-hidden">
                      <div className="h-full gradient-brand rounded-full" style={{ width: `${item.score}%` }} />
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          {/* Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-primary" />
                Timeline Rencana Aksi
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {plan.timeline.map((phase) => (
                <div key={phase.phase}>
                  <h4 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wider">{phase.phase}</h4>
                  <div className="space-y-2">
                    {phase.tasks.map((task) => (
                      <div key={task.task} className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ${
                          task.done ? "bg-success border-success" : "border-muted-foreground/30"
                        }`}>
                          {task.done && <CheckCircle2 className="h-3.5 w-3.5 text-white" />}
                        </div>
                        <div className="flex-1">
                          <div className="text-sm font-medium">{task.task}</div>
                          <div className="text-xs text-muted-foreground flex items-center gap-2 mt-0.5">
                            <Clock className="h-3 w-3" />
                            {task.deadline}
                          </div>
                        </div>
                        <Badge variant={task.priority === "high" ? "destructive" : task.priority === "medium" ? "warning" : "secondary"}>
                          {task.priority}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Documents */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Dokumen yang Diperlukan
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {plan.required_documents.map((doc) => (
                <div key={doc.name} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      doc.status === "ready" ? "bg-success" : doc.status === "need" ? "bg-warning" : "bg-muted-foreground"
                    }`} />
                    <div>
                      <div className="text-sm font-medium">{doc.name}</div>
                      {doc.notes && <div className="text-xs text-muted-foreground">{doc.notes}</div>}
                    </div>
                  </div>
                  <Badge variant={doc.status === "ready" ? "success" : doc.status === "need" ? "warning" : "secondary"}>
                    {doc.status === "ready" ? "Siap" : doc.status === "need" ? "Butuh" : "Opsional"}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-primary" />
                Rekomendasi
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {plan.recommendations.map((rec) => (
                  <li key={rec} className="flex items-start gap-2 text-sm">
                    <ChevronRight className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Risks */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-warning" />
                Risiko yang Perlu Diwaspadai
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {plan.risks.map((risk) => (
                <div key={risk.risk} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <span className="text-sm">{risk.risk}</span>
                  <div className="flex gap-2">
                    <Badge variant={risk.probability === "high" ? "destructive" : "warning"} className="text-xs">
                      {risk.probability}
                    </Badge>
                    <Badge variant={risk.impact === "high" ? "destructive" : "warning"} className="text-xs">
                      {risk.impact}
                    </Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {!plan && !isLoading && (
        <div className="text-center py-20">
          <ClipboardList className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">Belum ada rencana aksi</h3>
          <p className="text-sm text-muted-foreground">
            Deskripsikan situasi Anda di atas untuk mendapatkan rencana aksi personal
          </p>
        </div>
      )}
    </div>
  )
}
