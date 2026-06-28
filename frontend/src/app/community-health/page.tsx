"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { mockAnalyticsData } from "@/lib/mock-data"
import {
  Globe,
  TrendingUp,
  TrendingDown,
  Users,
  Heart,
  GraduationCap,
  Accessibility,
  HandHeart,
  MapPin,
} from "lucide-react"

const categoryIcons: Record<string, typeof Heart> = {
  education: GraduationCap,
  health: Heart,
  social: HandHeart,
  accessibility: Accessibility,
}

const categoryLabels: Record<string, string> = {
  education: "Pendidikan",
  health: "Kesehatan",
  social: "Sosial",
  accessibility: "Aksesibilitas",
}

const categoryColors: Record<string, string> = {
  education: "from-cyan-500 to-blue-500",
  health: "from-green-500 to-teal-500",
  social: "from-purple-500 to-pink-500",
  accessibility: "from-amber-500 to-orange-500",
}

export default function CommunityHealthPage() {
  const data = mockAnalyticsData
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null)

  const sortedRegions = Object.entries(data.regional_scores).sort((a, b) => {
    const avgA = (a[1].education + a[1].health + a[1].social + a[1].accessibility) / 4
    const avgB = (b[1].education + b[1].health + b[1].social + b[1].accessibility) / 4
    return avgB - avgA
  })

  const topRegion = sortedRegions[0]
  const bottomRegion = sortedRegions[sortedRegions.length - 1]

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 py-8 space-y-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Community Health Score</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Skor kesehatan komunitas berdasarkan pendidikan, kesehatan, dukungan sosial, dan aksesibilitas per regional
          </p>
        </div>

        {/* National Overview */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Total Wilayah", value: Object.keys(data.regional_scores).length, icon: Globe, color: "text-blue-500" },
            { label: "Tertinggi", value: topRegion[0], icon: TrendingUp, color: "text-green-500", score: Math.round((topRegion[1].education + topRegion[1].health + topRegion[1].social + topRegion[1].accessibility) / 4) },
            { label: "Terendah", value: bottomRegion[0], icon: TrendingDown, color: "text-red-500", score: Math.round((bottomRegion[1].education + bottomRegion[1].health + bottomRegion[1].social + bottomRegion[1].accessibility) / 4) },
            { label: "Rata-rata Nasional", value: "65.8", icon: Users, color: "text-purple-500" },
          ].map((item) => {
            const Icon = item.icon
            return (
              <Card key={item.label}>
                <CardContent className="p-5">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">{item.label}</p>
                      <p className="text-xl font-bold mt-1">{item.value}</p>
                    </div>
                    <Icon className={`h-5 w-5 ${item.color}`} />
                  </div>
                  {"score" in item && item.score && (
                    <div className="flex items-center gap-1 mt-2">
                      <Badge variant={item.score > 70 ? "success" : item.score > 55 ? "warning" : "destructive"}>
                        Skor: {item.score}
                      </Badge>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Regional Grid */}
        <div className="grid lg:grid-cols-2 gap-4">
          {sortedRegions.map(([region, scores], idx) => {
            const avg = Math.round((scores.education + scores.health + scores.social + scores.accessibility) / 4)
            const isSelected = selectedRegion === region
            return (
              <motion.div
                key={region}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <Card
                  className={`cursor-pointer transition-all duration-200 hover:shadow-md ${isSelected ? "ring-2 ring-primary" : ""
                    }`}
                  onClick={() => setSelectedRegion(isSelected ? null : region)}
                >
                  <CardContent className="p-5">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-primary" />
                        <h3 className="font-semibold">{region}</h3>
                      </div>
                      <Badge variant={avg > 70 ? "success" : avg > 55 ? "warning" : "destructive"}>
                        Skor {avg}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-4 gap-3">
                      {(Object.keys(categoryLabels) as Array<keyof typeof categoryLabels>).map((key) => {
                        const Icon = categoryIcons[key]
                        const score = scores[key as keyof typeof scores]
                        return (
                          <div key={key} className="text-center">
                            <div className={`w-8 h-8 mx-auto rounded-lg bg-gradient-to-br ${categoryColors[key]} p-1.5 mb-1.5`}>
                              <Icon className="h-full w-full text-white" />
                            </div>
                            <div className="text-xs text-muted-foreground">{categoryLabels[key]}</div>
                            <div className="text-sm font-bold">{score}</div>
                            <div className="h-1 bg-muted rounded-full mt-1 overflow-hidden">
                              <div
                                className="h-full gradient-brand rounded-full transition-all duration-500"
                                style={{ width: `${score}%` }}
                              />
                            </div>
                          </div>
                        )
                      })}
                    </div>
                    {isSelected && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        className="mt-4 pt-4 border-t"
                      >
                        <p className="text-sm text-muted-foreground">
                          {region} memiliki skor pendidikan {scores.education}, kesehatan {scores.health},
                          dukungan sosial {scores.social}, dan aksesibilitas {scores.accessibility}.
                          {avg > 70
                            ? " Wilayah ini menunjukkan performa komunitas yang baik."
                            : avg > 55
                              ? " Wilayah ini memerlukan perhatian pada beberapa sektor."
                              : " Wilayah ini memerlukan intervensi signifikan untuk meningkatkan kualitas hidup warga."}
                        </p>
                      </motion.div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </div>
      </motion.div>
    </div>
  )
}
