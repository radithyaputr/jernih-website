"use client"

import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  ShieldCheck,
  Brain,
  Lock,
  Scale,
  Eye,
  Users,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  FileText,
} from "lucide-react"

const principles = [
  {
    icon: Eye,
    title: "Transparansi",
    desc: "Setiap output AI dijelaskan secara jelas termasuk sumber data, metode, dan tingkat kepercayaan.",
    color: "from-cyan-500 to-blue-500",
  },
  {
    icon: Scale,
    title: "Keadilan",
    desc: "AI dirancang untuk tidak memihak dan memberikan layanan yang setara untuk semua warga negara.",
    color: "from-purple-500 to-pink-500",
  },
  {
    icon: Lock,
    title: "Privasi",
    desc: "Data pribadi warga dilindungi. Kami tidak menyimpan informasi sensitif tanpa izin eksplisit.",
    color: "from-green-500 to-teal-500",
  },
  {
    icon: RefreshCw,
    title: "Akuntabilitas",
    desc: "Setiap rekomendasi dapat dilacak, diaudit, dan ditinjau oleh manusia.",
    color: "from-amber-500 to-orange-500",
  },
  {
    icon: Users,
    title: "Inklusivitas",
    desc: "Layanan dapat diakses oleh semua warga termasuk penyandang disabilitas dan masyarakat rural.",
    color: "from-rose-500 to-red-500",
  },
  {
    icon: ShieldCheck,
    title: "Keamanan",
    desc: "Sistem dilindungi dari serangan prompt injection, manipulasi, dan akses tidak sah.",
    color: "from-violet-500 to-indigo-500",
  },
]

const trustComponents = [
  { label: "Reliability Score", desc: "Seberapa andal informasi berdasarkan sumber resmi", icon: ShieldCheck },
  { label: "Freshness Score", desc: "Seberapa baru data yang digunakan", icon: RefreshCw },
  { label: "Verification Score", desc: "Seberapa terverifikasi informasi dengan data pemerintah", icon: CheckCircle2 },
  { label: "Transparency Score", desc: "Seberapa transparan proses pengambilan keputusan AI", icon: Eye },
]

export default function ResponsibleAIPage() {
  return (
    <div className="mx-auto max-w-5xl px-4 sm:px-6 py-8 space-y-10">
      {/* Hero */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="text-center py-8">
        <Badge variant="brand" className="mb-4 px-4 py-1.5">
          <ShieldCheck className="h-4 w-4 mr-1.5" />
          Responsible AI by Default
        </Badge>
        <h1 className="text-3xl sm:text-4xl font-bold mb-4">Responsible AI Center</h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
          JERNIH dibangun dengan prinsip Responsible AI — transparan, adil, aman, dan
          dapat dipercaya oleh setiap warga Indonesia.
        </p>
      </motion.div>

      {/* Principles */}
      <section>
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Scale className="h-5 w-5 text-primary" />
          Prinsip Responsible AI
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {principles.map((p) => {
            const Icon = p.icon
            return (
              <motion.div
                key={p.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="p-6 rounded-xl border bg-card hover:shadow-md transition-all"
              >
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${p.color} p-2 mb-4`}>
                  <Icon className="h-full w-full text-white" />
                </div>
                <h3 className="font-semibold mb-2">{p.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{p.desc}</p>
              </motion.div>
            )
          })}
        </div>
      </section>

      {/* Trust Score Components */}
      <section>
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-primary" />
          Komponen Trust Score
        </h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {trustComponents.map((tc) => {
            const Icon = tc.icon
            return (
              <Card key={tc.label}>
                <CardContent className="p-5 flex items-start gap-4">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm">{tc.label}</h4>
                    <p className="text-sm text-muted-foreground mt-1">{tc.desc}</p>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </section>

      {/* How AI Works */}
      <section>
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          Bagaimana AI Bekerja
        </h2>
        <Card>
          <CardContent className="p-6 space-y-4">
            <div className="space-y-4">
              {[
                { step: 1, title: "Input & Analisis Konteks", desc: "AI menganalisis masukan pengguna untuk memahami konteks, kebutuhan, dan situasi spesifik." },
                { step: 2, title: "Retrieval Informasi", desc: "Sistem mencari informasi dari basis pengetahuan yang berisi data resmi pemerintah, regulasi, dan program." },
                { step: 3, title: "Verifikasi & Validasi", desc: "Setiap informasi diverifikasi terhadap sumber resmi dan data pemerintah terkini." },
                { step: 4, title: "Generasi Respons", desc: "AI menghasilkan respons yang informatif, akurat, dan bertanggung jawab." },
                { step: 5, title: "Penambahan Trust Score", desc: "Setiap respons dilengkapi dengan skor kepercayaan, sumber, dan penjelasan." },
              ].map((item) => (
                <div key={item.step} className="flex gap-4">
                  <div className="w-8 h-8 rounded-full gradient-brand text-white text-sm font-bold flex items-center justify-center shrink-0">
                    {item.step}
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm">{item.title}</h4>
                    <p className="text-sm text-muted-foreground">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* AI Limitations */}
      <section>
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-warning" />
          Keterbatasan AI
        </h2>
        <Card>
          <CardContent className="p-6 space-y-3">
            {[
              "AI dapat memberikan informasi yang tidak akurat jika data sumber tidak lengkap atau kedaluwarsa",
              "AI tidak dapat menggantikan konsultasi dengan pejabat pemerintah atau ahli hukum",
              "Keputusan akhir tetap berada di tangan pengguna dan pejabat berwenang",
              "AI tidak menyimpan data pribadi pengguna secara permanen",
              "Beberapa program memiliki persyaratan yang berubah-ubah sesuai kebijakan terkini",
            ].map((limitation) => (
              <div key={limitation} className="flex items-start gap-2 text-sm">
                <AlertTriangle className="h-4 w-4 text-warning mt-0.5 shrink-0" />
                <span className="text-muted-foreground">{limitation}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>

      {/* Data Sources */}
      <section>
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <FileText className="h-5 w-5 text-primary" />
          Sumber Data
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            { name: "BPS", desc: "Badan Pusat Statistik" },
            { name: "Kemensos", desc: "Kementerian Sosial" },
            { name: "BNPB", desc: "Badan Nasional Penanggulangan Bencana" },
            { name: "Kemdikdasmen", desc: "Kementerian Pendidikan" },
            { name: "Komdigi", desc: "Kementerian Komdigi" },
            { name: "Open Data ID", desc: "Portal Data Terbuka Indonesia" },
            { name: "WHO", desc: "World Health Organization" },
            { name: "UNICEF", desc: "United Nations Children's Fund" },
          ].map((src) => (
            <div key={src.name} className="p-4 rounded-xl border bg-card text-center">
              <div className="font-semibold">{src.name}</div>
              <div className="text-xs text-muted-foreground mt-1">{src.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Privacy */}
      <section>
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <Lock className="h-5 w-5 text-primary" />
          Privasi & Keamanan Data
        </h2>
        <Card>
          <CardContent className="p-6 space-y-4">
            {[
              "Kami tidak menyimpan data pribadi pengguna (NIK, alamat, dll) secara permanen",
              "Semua data ditransmisikan dengan enkripsi end-to-end",
              "Pengguna dapat meminta penghapusan data kapan saja",
              "Sistem mematuhi regulasi perlindungan data Indonesia (UU PDP)",
              "Audit keamanan dilakukan secara berkala oleh pihak ketiga",
            ].map((item) => (
              <div key={item} className="flex items-start gap-3 text-sm">
                <CheckCircle2 className="h-4 w-4 text-success mt-0.5 shrink-0" />
                <span>{item}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
