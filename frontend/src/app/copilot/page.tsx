"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Brain,
  Send,
  AlertTriangle,
  CheckCircle2,
  Clock,
  FileText,
  Building2,
  TrendingUp,
  ShieldCheck,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Loader2,
  WifiOff,
} from "lucide-react"
import { api } from "@/lib/api"
import type { CopilotAnyResponse, CopilotAnalysisResponse } from "@/lib/api"

const suggestions = [
  "Ayah saya meninggal, apa yang harus saya urus?",
  "Saya ingin mendaftar KIP",
  "Saya kehilangan KTP",
  "Saya ingin cari bantuan pendidikan",
]

type Message = {
  id: string
  role: "user" | "assistant"
  content: string
  data?: CopilotAnyResponse
  isError?: boolean
}

const quickPrograms = [
  { name: "PIP", desc: "Bantuan pendidikan", color: "from-cyan-500 to-blue-500" },
  { name: "KIS", desc: "Jaminan kesehatan", color: "from-green-500 to-teal-500" },
  { name: "BPNT", desc: "Bantuan pangan", color: "from-orange-500 to-red-500" },
  { name: "PKH", desc: "Bantuan keluarga", color: "from-purple-500 to-pink-500" },
]

export default function CopilotPage() {
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Halo! Saya adalah AI Civic Copilot JERNIH. Ceritakan situasi Anda, dan saya akan membantu menemukan solusi, program, dan dokumen yang Anda perlukan. ✨",
    },
  ])
  const [isLoading, setIsLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || isLoading) return
    const userMsg: Message = { id: Date.now().toString(), role: "user", content: input }
    setMessages((prev) => [...prev, userMsg])
    setInput("")
    setIsLoading(true)

    try {
      console.log("Calling API with message:", input)
      const res = await api.copilot.chat({ message: input })
      console.log("API response received:", res)

      if (res.type === "casual") {
        // Casual response — just a text message
        const assistantMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: res.message,
        }
        setMessages((prev) => [...prev, assistantMsg])
      } else {
        // Analysis response — full data
        const assistantMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "",
          data: res,
        }
        setMessages((prev) => [...prev, assistantMsg])
      }
    } catch (error) {
      console.error("Error in copilot:", error)
      // Show user-friendly error — NO mock data fallback
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Maaf, saya tidak dapat terhubung ke server saat ini. Pastikan backend sudah berjalan di http://localhost:8000, lalu coba lagi. 🔌",
        isError: true,
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex">
      {/* Main Chat */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-4">
        <div className="flex-1 overflow-y-auto py-6 space-y-6">
          <AnimatePresence>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
              >
                <Avatar className={`h-8 w-8 mt-1 shrink-0 ${msg.role === "assistant" ? "" : ""}`}>
                  <AvatarFallback className={msg.role === "assistant" ? "gradient-brand text-white text-xs" : "bg-primary/10 text-primary text-xs"}>
                    {msg.role === "assistant" ? "JN" : "WN"}
                  </AvatarFallback>
                </Avatar>
                <div className={`max-w-[85%] ${msg.role === "user" ? "text-right" : ""}`}>
                  {msg.role === "user" ? (
                    <div className="inline-block bg-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm">
                      {msg.content}
                    </div>
                  ) : msg.isError ? (
                    /* Error message with warning styling */
                    <div className="glass rounded-2xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed border border-destructive/30">
                      <div className="flex items-start gap-2">
                        <WifiOff className="h-4 w-4 text-destructive mt-0.5 shrink-0" />
                        <span>{msg.content}</span>
                      </div>
                    </div>
                  ) : msg.data && msg.data.type === "analysis" ? (
                    /* Analysis response — full card UI */
                    <CopilotResponseView data={msg.data} />
                  ) : (
                    /* Casual/text response — simple bubble */
                    <div className="glass rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm leading-relaxed">
                      {msg.content}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-3"
              >
                <Avatar className="h-8 w-8 mt-1 shrink-0">
                  <AvatarFallback className="gradient-brand text-white text-xs">JN</AvatarFallback>
                </Avatar>
                <div className="glass rounded-2xl rounded-tl-sm px-4 py-3">
                  <Loader2 className="h-5 w-5 animate-spin text-primary" />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Suggestions */}
        {messages.length === 1 && (
          <div className="mb-4">
            <p className="text-xs text-muted-foreground mb-2 font-medium">Coba tanyakan:</p>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => { setInput(s) }}
                  className="text-xs px-3 py-1.5 rounded-full border bg-card hover:bg-accent hover:border-primary/30 transition-all text-muted-foreground hover:text-foreground"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="sticky bottom-0 pb-4 pt-2 bg-gradient-to-t from-background via-background to-transparent">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ceritakan situasi Anda..."
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              className="rounded-xl h-12 px-4 text-sm"
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              variant="brand"
              size="icon"
              className="h-12 w-12 shrink-0 rounded-xl"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
          <p className="text-[10px] text-muted-foreground text-center mt-2">
            JERNIH menggunakan Responsible AI. Jawaban dilengkapi skor kepercayaan dan sumber.
          </p>
        </div>
      </div>

      {/* Quick Panel */}
      <div className="hidden xl:block w-72 border-l p-4 space-y-3 overflow-y-auto">
        <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          Program Populer
        </div>
        {quickPrograms.map((p) => (
          <div key={p.name} className="flex items-center gap-3 p-3 rounded-xl border bg-card hover:shadow-sm transition-all cursor-pointer">
            <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${p.color} p-1.5 shrink-0`}>
              <Sparkles className="h-full w-full text-white" />
            </div>
            <div>
              <div className="text-sm font-medium">{p.name}</div>
              <div className="text-xs text-muted-foreground">{p.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function CopilotResponseView({ data }: { data: CopilotAnalysisResponse }) {
  const r = data.response

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="glass rounded-2xl rounded-tl-sm p-5">
        <div className="flex items-start gap-3 mb-3">
          <div className="gradient-brand rounded-lg p-1.5 mt-0.5 shrink-0">
            <Brain className="h-4 w-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-sm">Analisis Situasi</h3>
            <p className="text-sm text-muted-foreground mt-1 leading-relaxed">{r.summary}</p>
          </div>
        </div>
        <p className="text-sm text-muted-foreground leading-relaxed ml-10">{r.analysis}</p>
      </div>

      {/* Trust & Success Score */}
      <div className="flex gap-3">
        {[
          { label: "Skor Kepercayaan", score: r.trust_score.overall, icon: ShieldCheck, color: "text-cyan-500" },
          { label: "Probabilitas Sukses", score: r.success_probability, icon: TrendingUp, color: "text-green-500" },
        ].map((item) => {
          const Icon = item.icon
          return (
            <div key={item.label} className="flex-1 glass rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`h-4 w-4 ${item.color}`} />
                <span className="text-xs text-muted-foreground">{item.label}</span>
              </div>
              <div className="text-2xl font-bold">{item.score}<span className="text-sm text-muted-foreground">/100</span></div>
            </div>
          )
        })}
      </div>

      {/* Relevant Programs */}
      <div className="glass rounded-xl p-5">
        <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          Program yang Relevan
        </h4>
        <div className="space-y-2">
          {r.relevant_programs.map((prog) => (
            <div key={prog.name} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <div>
                <div className="text-sm font-medium">{prog.name}</div>
                <div className="text-xs text-muted-foreground">{prog.agency} — {prog.description}</div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={prog.match_score > 85 ? "success" : prog.match_score > 70 ? "warning" : "secondary"}>
                  {prog.match_score}% cocok
                </Badge>
                {prog.url && (
                  <a href={prog.url} target="_blank" rel="noreferrer">
                    <ExternalLink className="h-3.5 w-3.5 text-muted-foreground hover:text-primary transition-colors" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Required Documents */}
      <div className="glass rounded-xl p-5">
        <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <FileText className="h-4 w-4 text-primary" />
          Dokumen yang Diperlukan
        </h4>
        <div className="space-y-2">
          {r.required_documents.map((doc) => (
            <div key={doc.name} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <div className="flex items-center gap-3">
                <CheckCircle2 className={`h-4 w-4 ${doc.priority === "high" ? "text-destructive" : doc.priority === "medium" ? "text-warning" : "text-muted-foreground"}`} />
                <div>
                  <div className="text-sm font-medium">{doc.name}</div>
                  <div className="text-xs text-muted-foreground">{doc.description}</div>
                </div>
              </div>
              <Badge variant={doc.priority === "high" ? "destructive" : doc.priority === "medium" ? "warning" : "secondary"}>
                {doc.priority === "high" ? "Prioritas" : doc.priority === "medium" ? "Penting" : "Opsional"}
              </Badge>
            </div>
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div className="glass rounded-xl p-5">
        <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <Clock className="h-4 w-4 text-primary" />
          Timeline — Estimasi {r.timeline.estimated_days} Hari
        </h4>
        <div className="space-y-0">
          {r.timeline.steps.map((step) => (
            <div key={step.step} className="flex gap-3 pb-4 last:pb-0 relative">
              <div className="flex flex-col items-center">
                <div className="w-6 h-6 rounded-full gradient-brand text-white text-xs font-bold flex items-center justify-center shrink-0">
                  {step.step}
                </div>
                {step.step < r.timeline.steps.length && (
                  <div className="w-px flex-1 bg-border mt-1" />
                )}
              </div>
              <div className="flex-1 pt-0.5">
                <div className="text-sm font-medium">{step.action}</div>
                <div className="text-xs text-muted-foreground flex items-center gap-2 mt-0.5">
                  <Clock className="h-3 w-3" />
                  {step.duration}
                  {step.office !== "-" && (
                    <>
                      <Building2 className="h-3 w-3 ml-2" />
                      {step.office}
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Action Plan */}
      <div className="glass rounded-xl p-5">
        <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-primary" />
          Rencana Aksi
        </h4>
        <div className="grid sm:grid-cols-3 gap-3">
          {[
            { title: "Hari Ini", items: r.action_plan.today },
            { title: "Minggu Ini", items: r.action_plan.this_week },
            { title: "Selanjutnya", items: r.action_plan.next_step },
          ].map((phase) => (
            <div key={phase.title} className="p-3 rounded-lg bg-muted/50">
              <div className="text-xs font-semibold text-muted-foreground mb-2 uppercase tracking-wider">{phase.title}</div>
              <ul className="space-y-1.5">
                {phase.items.map((item) => (
                  <li key={item} className="text-sm flex items-start gap-2">
                    <ChevronRight className="h-3.5 w-3.5 text-primary mt-0.5 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Factors */}
      <div className="glass rounded-xl p-5">
        <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-warning" />
          Faktor Risiko
        </h4>
        <div className="space-y-2">
          {r.risk_factors.map((risk) => (
            <div key={risk.risk} className="p-3 rounded-lg bg-muted/50">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2">
                  <AlertTriangle className={`h-4 w-4 mt-0.5 shrink-0 ${risk.severity === "high" ? "text-destructive" : risk.severity === "medium" ? "text-warning" : "text-muted-foreground"}`} />
                  <div>
                    <div className="text-sm font-medium">{risk.risk}</div>
                    <div className="text-xs text-muted-foreground mt-0.5">{risk.mitigation}</div>
                  </div>
                </div>
                <Badge variant={risk.severity === "high" ? "destructive" : risk.severity === "medium" ? "warning" : "secondary"}>
                  {risk.severity}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Sources */}
      <div className="glass rounded-xl p-5">
        <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-primary" />
          Sumber Informasi
        </h4>
        <div className="space-y-2">
          {r.sources.map((src) => (
            <div key={src.title} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50 transition-colors">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-success" />
                <span className="text-sm">{src.title}</span>
              </div>
              <Badge variant="secondary" className="text-xs">{src.type}</Badge>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

