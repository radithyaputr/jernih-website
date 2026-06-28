"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import {
  Search,
  ArrowRight,
  CheckCircle2,
  Clock,
  Building2,
  FileCheck,
  AlertTriangle,
  ChevronRight,
  Lightbulb,
  Loader2,
} from "lucide-react"

interface SimplifiedProcedure {
  title: string
  original_text: string
  simple_language: string
  steps: Array<{
    step: number
    action: string
    details: string
    office?: string
    duration?: string
    tips?: string
  }>
  checklist: Array<{
    item: string
    important: boolean
  }>
  estimated_time: string
  complexity_score: number
  risks: string[]
}

const mockProcedure: SimplifiedProcedure = {
  title: "Pembuatan KTP Elektronik",
  original_text: "Persyaratan dan tata cara permohonan KTP elektronik sebagaimana diatur dalam...",
  simple_language: "KTP Elektronik adalah kartu identitas resmi warga negara Indonesia yang wajib dimiliki setiap warga yang telah berusia 17 tahun atau sudah menikah.",
  steps: [
    {
      step: 1,
      action: "Datang ke Kantor Dukcapil Kecamatan",
      details: "Bawa dokumen lengkap ke lokasi terdekat. Pastikan datang pada jam kerja (Senin-Jumat, 08:00-15:00).",
      office: "Kantor Kecamatan",
      duration: "1 hari",
      tips: "Datang pagi hari untuk menghindari antrean panjang",
    },
    {
      step: 2,
      action: "Ambil nomor antrean",
      details: "Ambil nomor antrean di mesin antrean atau loket pendaftaran.",
      office: "Kantor Kecamatan",
      duration: "5-10 menit",
    },
    {
      step: 3,
      action: "Serahkan dokumen ke petugas",
      details: "Petugas akan memverifikasi dokumen dan memproses permohonan KTP elektronik.",
      office: "Kantor Kecamatan",
      duration: "30 menit",
      tips: "Pastikan semua dokumen sudah difotokopi",
    },
    {
      step: 4,
      action: "Foto dan perekaman biometrik",
      details: "Petugas akan mengambil foto, sidik jari, dan tanda tangan elektronik.",
      office: "Kantor Kecamatan",
      duration: "15 menit",
    },
    {
      step: 5,
      action: "Tunggu proses pencetakan",
      details: "KTP Elektronik akan dicetak dan biasanya selesai pada hari yang sama atau maksimal 14 hari kerja.",
      office: "Kantor Kecamatan",
      duration: "1-14 hari",
      tips: "Beberapa daerah menawarkan layanan antar ke rumah",
    },
  ],
  checklist: [
    { item: "Fotokopi Kartu Keluarga (KK) 1 lembar", important: true },
    { item: "Fotokopi Akta Kelahiran (jika ada)", important: false },
    { item: "Surat pengantar dari RT/RW", important: true },
    { item: "Mengisi formulir permohonan (disediakan)", important: true },
    { item: "Pas foto 3x4 (4 lembar, background merah)", important: true },
  ],
  estimated_time: "1-14 hari kerja",
  complexity_score: 30,
  risks: [
    "Antrean panjang di awal bulan dan akhir tahun",
    "Dokumen tidak lengkap menyebabkan penundaan",
    "Sistem terkadang mengalami gangguan teknis",
    "Perbedaan data dengan database Dukcapil",
  ],
}

export default function ProcedureSimplifierPage() {
  const [search, setSearch] = useState("")
  const [procedure, setProcedure] = useState<SimplifiedProcedure | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = () => {
    if (!search.trim() || isLoading) return
    setIsLoading(true)
    setTimeout(() => {
      setProcedure(mockProcedure)
      setIsLoading(false)
    }, 800)
  }

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 py-8 space-y-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <h1 className="text-2xl font-bold">AI Procedure Simplifier</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Sederhanakan prosedur birokrasi yang rumit menjadi langkah mudah dipahami
          </p>
        </div>

        <Card>
          <CardContent className="p-6">
            <div className="flex gap-2">
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Cari prosedur publik, misal: 'buat KTP', 'urus KK', 'daftar PIP'..."
                className="rounded-xl h-12 px-4 text-sm"
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              />
              <Button onClick={handleSearch} disabled={!search.trim() || isLoading} variant="brand" size="xl" className="shrink-0">
                {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Search className="h-5 w-5" />}
                Cari
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {procedure && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold">{procedure.title}</h2>
              <p className="text-sm text-muted-foreground mt-2 max-w-2xl leading-relaxed">{procedure.simple_language}</p>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{procedure.complexity_score}</div>
              <div className="text-xs text-muted-foreground">Kompleksitas</div>
              <Badge variant={procedure.complexity_score > 50 ? "destructive" : "success"} className="mt-1">
                {procedure.complexity_score > 50 ? "Kompleks" : "Sederhana"}
              </Badge>
            </div>
          </div>

          {/* Steps */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ArrowRight className="h-5 w-5 text-primary" />
                Langkah-langkah
                <Badge variant="secondary" className="ml-auto">
                  Estimasi: {procedure.estimated_time}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-0">
                {procedure.steps.map((step) => (
                  <div key={step.step} className="flex gap-4 pb-6 last:pb-0 relative">
                    <div className="flex flex-col items-center">
                      <div className="w-8 h-8 rounded-full gradient-brand text-white text-sm font-bold flex items-center justify-center shrink-0">
                        {step.step}
                      </div>
                      {step.step < procedure.steps.length && <div className="w-px flex-1 bg-border mt-1" />}
                    </div>
                    <div className="flex-1 pt-0.5">
                      <h4 className="font-semibold text-sm">{step.action}</h4>
                      <p className="text-sm text-muted-foreground mt-1">{step.details}</p>
                      <div className="flex flex-wrap gap-3 mt-2">
                        {step.office && (
                          <span className="text-xs flex items-center gap-1 text-muted-foreground">
                            <Building2 className="h-3 w-3" />
                            {step.office}
                          </span>
                        )}
                        {step.duration && (
                          <span className="text-xs flex items-center gap-1 text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            {step.duration}
                          </span>
                        )}
                      </div>
                      {step.tips && (
                        <div className="mt-2 flex items-start gap-1.5 text-xs text-primary bg-primary/5 p-2 rounded-lg">
                          <Lightbulb className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                          <span>{step.tips}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Checklist */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileCheck className="h-5 w-5 text-primary" />
                Checklist Dokumen
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {procedure.checklist.map((item) => (
                <div key={item.item} className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                  <CheckCircle2 className={`h-4 w-4 ${item.important ? "text-destructive" : "text-muted-foreground"}`} />
                  <span className="text-sm">{item.item}</span>
                  {item.important && <Badge variant="destructive" className="text-xs ml-auto">WAJIB</Badge>}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Risks */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-warning" />
                Hal yang Perlu Diperhatikan
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {procedure.risks.map((risk) => (
                  <li key={risk} className="flex items-start gap-2 text-sm">
                    <ChevronRight className="h-4 w-4 text-warning mt-0.5 shrink-0" />
                    <span>{risk}</span>
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
