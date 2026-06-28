"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import {
  Brain,
  ShieldCheck,
  Share2,
  ClipboardList,
  Search,
  BarChart3,
  Globe,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Users,
  Clock,
  Target,
  TrendingUp,
  FileText,
} from "lucide-react"

const features = [
  {
    icon: Brain,
    title: "AI Civic Copilot",
    desc: "Asisten AI yang membantu memahami layanan publik, dokumen, dan prosedur pemerintahan.",
    href: "/copilot",
    color: "from-cyan-500 to-blue-500",
  },
  {
    icon: Share2,
    title: "Knowledge Graph",
    desc: "Visualisasi interaktif hubungan antara program, dokumen, dan instansi pemerintah.",
    href: "/knowledge-graph",
    color: "from-purple-500 to-pink-500",
  },
  {
    icon: ClipboardList,
    title: "Action Plan Generator",
    desc: "Rencana aksi personal untuk mengurus dokumen dan mengakses program bantuan.",
    href: "/action-plan",
    color: "from-green-500 to-teal-500",
  },
  {
    icon: Search,
    title: "Hoax Checker",
    desc: "Verifikasi informasi dan deteksi hoaks dengan analisis sumber terpercaya.",
    href: "/hoax-checker",
    color: "from-orange-500 to-red-500",
  },
  {
    icon: FileText,
    title: "Procedure Simplifier",
    desc: "Sederhanakan prosedur birokrasi yang rumit menjadi langkah mudah dipahami.",
    href: "/procedure-simplifier",
    color: "from-blue-500 to-indigo-500",
  },
  {
    icon: BarChart3,
    title: "Policy Simulator",
    desc: "Simulasi dampak perubahan kebijakan terhadap masyarakat Indonesia.",
    href: "/policy-simulator",
    color: "from-violet-500 to-purple-500",
  },
  {
    icon: Globe,
    title: "Community Health",
    desc: "Skor kesehatan komunitas berdasarkan pendidikan, kesehatan, dan aksesibilitas.",
    href: "/community-health",
    color: "from-emerald-500 to-green-500",
  },
  {
    icon: ShieldCheck,
    title: "Responsible AI",
    desc: "Transparansi AI, privasi data, dan prinsip etis dalam setiap rekomendasi.",
    href: "/responsible-ai",
    color: "from-rose-500 to-pink-500",
  },
]

const impactMetrics = [
  { icon: Users, value: "124.583", label: "Warga Dibantu", change: "+23%" },
  { icon: Clock, value: "81.500", label: "Jam Hemat", change: "+15%" },
  { icon: Target, value: "15.420", label: "Program Ditemukan", change: "+31%" },
  { icon: TrendingUp, value: "Rp15,78 M", label: "Dampak Ekonomi", change: "+45%" },
]

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative overflow-hidden border-b bg-gradient-to-b from-background via-background to-muted/30">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-primary/5 via-transparent to-transparent" />
        <div className="mx-auto max-w-7xl px-4 sm:px-6 pt-20 pb-24 sm:pt-28 sm:pb-32 relative">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="text-center max-w-3xl mx-auto">
            <Badge variant="brand" className="mb-6 px-4 py-1.5 text-sm">
              <Sparkles className="h-3.5 w-3.5 mr-1.5" />
              LKS 2026 AI EXHIBITION
            </Badge>
            <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold tracking-tight leading-tight mb-6">
              Informasi yang Terang,
              <br />
              <span className="text-gradient">Bukan yang Bising</span>
            </h1>
            <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
              JERNIH adalah AI Civic Operating System yang mengubah informasi publik
              menjadi kecerdasan warga — membantu Anda membuat keputusan lebih baik,
              mengakses layanan, dan menavigasi birokrasi dengan AI yang Bertanggung Jawab.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/copilot">
                <Button size="xl" variant="brand" className="w-full sm:w-auto">
                  <Brain className="h-5 w-5 mr-2" />
                  Mulai dengan AI Copilot
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
              </Link>
              <Link href="/dashboard">
                <Button size="xl" variant="outline" className="w-full sm:w-auto">
                  Lihat Dampak
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* Metrics */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-16"
          >
            {impactMetrics.map((metric) => {
              const Icon = metric.icon
              return (
                <Card key={metric.label} className="border-0 bg-white/50 dark:bg-white/5 backdrop-blur-sm">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-3">
                      <Icon className="h-5 w-5 text-primary" />
                      <Badge variant="success" className="text-xs">{metric.change}</Badge>
                    </div>
                    <div className="text-2xl font-bold">{metric.value}</div>
                    <div className="text-sm text-muted-foreground">{metric.label}</div>
                  </CardContent>
                </Card>
              )
            })}
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 sm:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Platform Civic AI <span className="text-gradient">Lengkap</span>
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Delapan lapisan kecerdasan untuk melayani warga, siswa, pencari kerja, dan pemerintah.
            </p>
          </motion.div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((feature, i) => {
              const Icon = feature.icon
              return (
                <Link key={feature.href} href={feature.href}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.05 }}
                    className="group relative p-6 rounded-xl border bg-card hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5 cursor-pointer h-full"
                  >
                    <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${feature.color} p-2 mb-4`}>
                      <Icon className="h-full w-full text-white" />
                    </div>
                    <h3 className="font-semibold mb-2 group-hover:text-primary transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{feature.desc}</p>
                  </motion.div>
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className="py-20 bg-muted/30 border-y">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
              <Badge variant="brand" className="mb-4">Responsible AI</Badge>
              <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                AI yang Dapat{" "}
                <span className="text-gradient">Dipercaya</span>
              </h2>
              <p className="text-muted-foreground text-lg mb-8 leading-relaxed">
                Setiap jawaban dilengkapi dengan skor kepercayaan, sumber yang terverifikasi,
                dan penjelasan yang transparan. Tidak ada black box.
              </p>
              <div className="space-y-4">
                {[
                  { icon: ShieldCheck, text: "Semua informasi dilengkapi sumber resmi" },
                  { icon: CheckCircle2, text: "Verifikasi otomatis dengan data pemerintah" },
                  { icon: Users, text: "Privasi warga adalah prioritas utama" },
                ].map((item) => {
                  const Icon = item.icon
                  return (
                    <div key={item.text} className="flex items-start gap-3">
                      <Icon className="h-5 w-5 text-primary mt-0.5 shrink-0" />
                      <span className="text-muted-foreground">{item.text}</span>
                    </div>
                  )
                })}
              </div>
              <Link href="/responsible-ai">
                <Button variant="outline" className="mt-8">
                  Pelajari Responsible AI di JERNIH
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </Link>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="glass rounded-2xl p-8 border">
                <div className="flex items-center gap-3 mb-6">
                  <div className="gradient-brand rounded-lg p-2">
                    <Brain className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <div className="font-medium">Trust Score</div>
                    <div className="text-sm text-muted-foreground">Skor Kepercayaan AI</div>
                  </div>
                  <div className="ml-auto text-right">
                    <div className="text-3xl font-bold text-gradient">92</div>
                    <div className="text-xs text-muted-foreground">/100</div>
                  </div>
                </div>
                <div className="space-y-3">
                  {[
                    { label: "Reliabilitas", score: 95 },
                    { label: "Kesegaran Data", score: 88 },
                    { label: "Verifikasi", score: 90 },
                    { label: "Transparansi", score: 94 },
                  ].map((item) => (
                    <div key={item.label}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-muted-foreground">{item.label}</span>
                        <span className="font-medium">{item.score}/100</span>
                      </div>
                      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          whileInView={{ width: `${item.score}%` }}
                          viewport={{ once: true }}
                          transition={{ duration: 1, delay: 0.3 }}
                          className="h-full gradient-brand rounded-full"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="gradient-brand rounded-lg p-1.5">
                <Brain className="h-4 w-4 text-white" />
              </div>
              <span className="font-bold">JERNIH</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Grand Final LKS Nasional AI Exhibition 2026 — Built with Responsible AI
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
