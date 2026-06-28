"use client"

import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Users,
  Clock,
  Target,
  TrendingUp,
  ArrowUp,
  ArrowDown,
  ShieldCheck,
  Brain,
  Sparkles,
} from "lucide-react"
import { mockAnalyticsData } from "@/lib/mock-data"
import { formatNumber } from "@/lib/utils"

export default function DashboardPage() {
  const data = mockAnalyticsData

  const metrics = [
    { icon: Users, label: "Warga Dibantu", value: formatNumber(data.total_citizens_served), change: "+23%", color: "text-blue-500" },
    { icon: Clock, label: "Jam Dihemat", value: formatNumber(Math.round(data.total_time_saved_minutes / 60)), change: "+15%", color: "text-green-500" },
    { icon: Target, label: "Program Ditemukan", value: formatNumber(data.total_programs_discovered), change: "+31%", color: "text-purple-500" },
    { icon: TrendingUp, label: "Dampak Ekonomi", value: `Rp${(data.estimated_economic_impact / 1e9).toFixed(1)}M`, change: "+45%", color: "text-amber-500" },
  ]

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 py-8 space-y-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">National Dashboard</h1>
            <p className="text-muted-foreground text-sm mt-1">Real-time civic intelligence metrics</p>
          </div>
          <Badge variant="brand" className="px-3 py-1.5">
            <Sparkles className="h-3.5 w-3.5 mr-1.5" />
            Live Data
          </Badge>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((metric) => {
            const Icon = metric.icon
            return (
              <Card key={metric.label}>
                <CardContent className="p-5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">{metric.label}</p>
                      <p className="text-2xl font-bold mt-1">{metric.value}</p>
                    </div>
                    <div className={`p-2 rounded-lg bg-muted`}>
                      <Icon className={`h-5 w-5 ${metric.color}`} />
                    </div>
                  </div>
                  <div className="flex items-center gap-1 mt-3 text-xs text-success">
                    <ArrowUp className="h-3 w-3" />
                    {metric.change} dari bulan lalu
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </motion.div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Trust & Success Score */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <ShieldCheck className="h-5 w-5 text-primary" />
                Skor Kepercayaan & Keberhasilan
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                {[
                  { label: "Trust Score", score: data.average_trust_score, color: "from-cyan-500 to-blue-500" },
                  { label: "Citizen Success", score: data.average_success_score, color: "from-green-500 to-teal-500" },
                ].map((item) => (
                  <div key={item.label} className="text-center">
                    <div className="relative w-28 h-28 mx-auto mb-3">
                      <svg className="w-full h-full" viewBox="0 0 120 120">
                        <circle cx="60" cy="60" r="54" fill="none" stroke="hsl(214.3 31.8% 91.4%)" strokeWidth="8" />
                        <motion.circle
                          cx="60" cy="60" r="54" fill="none"
                          stroke="url(#grad)"
                          strokeWidth="8" strokeLinecap="round"
                          initial={{ pathLength: 0 }}
                          animate={{ pathLength: item.score / 100 }}
                          transition={{ duration: 1.5, delay: 0.3 }}
                          transform="rotate(-90 60 60)"
                        />
                        <defs>
                          <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="var(--color-brand)" />
                            <stop offset="100%" stopColor="var(--color-primary)" />
                          </linearGradient>
                        </defs>
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-3xl font-bold">{item.score}</span>
                      </div>
                    </div>
                    <p className="text-sm font-medium">{item.label}</p>
                    <p className="text-xs text-muted-foreground">Rata-rata seluruh pengguna</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Top Concerns */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Brain className="h-5 w-5 text-primary" />
                Top Keprihatinan Warga
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {data.top_concerns.map((concern) => (
                <div key={concern.issue} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <span className="text-sm font-medium">{concern.issue}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-muted-foreground">{formatNumber(concern.count)}</span>
                    <Badge variant={concern.growth > 30 ? "destructive" : "warning"} className="text-xs">
                      <ArrowUp className="h-3 w-3 mr-0.5" />
                      {concern.growth}%
                    </Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>

        {/* Community Trends */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <TrendingUp className="h-5 w-5 text-primary" />
                Tren Komunitas
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {data.community_trends.map((trend) => (
                <div key={trend.category} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <span className="text-sm font-medium">{trend.category}</span>
                  <div className="flex items-center gap-2">
                    <Badge variant={trend.direction === "up" ? "success" : "destructive"} className="text-xs">
                      {trend.direction === "up" ? <ArrowUp className="h-3 w-3 mr-0.5" /> : <ArrowDown className="h-3 w-3 mr-0.5" />}
                      {trend.change}%
                    </Badge>
                    <span className="text-xs text-muted-foreground">{trend.period}</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>

        {/* Regional Scores */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Users className="h-5 w-5 text-primary" />
                Skor Regional
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(data.regional_scores).slice(0, 6).map(([region, scores]) => {
                  const avg = Math.round((scores.education + scores.health + scores.social + scores.accessibility) / 4)
                  return (
                    <div key={region} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/50 transition-colors">
                      <span className="text-sm font-medium w-32">{region}</span>
                      <div className="flex gap-2 flex-1">
                        {[
                          { label: "Pendidikan", value: scores.education },
                          { label: "Kesehatan", value: scores.health },
                          { label: "Sosial", value: scores.social },
                          { label: "Akses", value: scores.accessibility },
                        ].map((s) => (
                          <div key={s.label} className="flex-1 text-center">
                            <div className="text-xs text-muted-foreground">{s.label}</div>
                            <div className="h-1.5 bg-muted rounded-full mt-1 overflow-hidden">
                              <div
                                className="h-full gradient-brand rounded-full transition-all duration-500"
                                style={{ width: `${s.value}%` }}
                              />
                            </div>
                            <div className="text-xs font-medium mt-0.5">{s.value}</div>
                          </div>
                        ))}
                      </div>
                      <Badge variant={avg > 70 ? "success" : avg > 55 ? "warning" : "destructive"} className="text-xs ml-2">
                        {avg}
                      </Badge>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
