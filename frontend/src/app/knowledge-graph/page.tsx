"use client"

import { useState, useRef, useCallback, useMemo } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { mockKnowledgeGraphData } from "@/lib/mock-data"
import {
  Share2,
  Search,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Info,
  X,
} from "lucide-react"

const typeColors: Record<string, string> = {
  program: "from-cyan-500 to-blue-500",
  agency: "from-purple-500 to-pink-500",
  document: "from-amber-500 to-orange-500",
  benefit: "from-green-500 to-teal-500",
  location: "from-rose-500 to-red-500",
  requirement: "from-violet-500 to-indigo-500",
}

const typeLabels: Record<string, string> = {
  program: "Program",
  agency: "Instansi",
  document: "Dokumen",
  benefit: "Manfaat",
  location: "Lokasi",
  requirement: "Persyaratan",
}

export default function KnowledgeGraphPage() {
  const data = mockKnowledgeGraphData
  const [search, setSearch] = useState("")
  const [selectedNode, setSelectedNode] = useState<typeof data.nodes[0] | null>(null)
  const [scale, setScale] = useState(1)
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 })

  const filteredNodes = search
    ? data.nodes.filter(n => n.label.toLowerCase().includes(search.toLowerCase()) || n.description?.toLowerCase().includes(search.toLowerCase()))
    : data.nodes

  const filteredLinks = search
    ? data.links.filter(l =>
        data.nodes.some(n => n.id === l.source && filteredNodes.some(fn => fn.id === n.id)) ||
        data.nodes.some(n => n.id === l.target && filteredNodes.some(fn => fn.id === n.id))
      )
    : data.links

  // Simple force-directed layout simulation (manual positions)
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)

  const positions = useMemo(() => {
    const pos = new Map<string, { x: number; y: number }>()
    if (!dimensions.width || !dimensions.height) return pos
    const cx = dimensions.width / 2
    const cy = dimensions.height / 2
    const radius = Math.min(cx, cy) * 0.7

    data.nodes.forEach((node, i) => {
      const angle = (i / data.nodes.length) * 2 * Math.PI - Math.PI / 2
      pos.set(node.id, {
        x: cx + radius * Math.cos(angle),
        y: cy + radius * Math.sin(angle),
      })
    })

    // Slight adjustments based on connections
    for (let iter = 0; iter < 50; iter++) {
      for (const link of data.links) {
        const source = pos.get(link.source)
        const target = pos.get(link.target)
        if (!source || !target) continue
        const dx = target.x - source.x
        const dy = target.y - source.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const force = (dist - 80) * 0.05
        const fx = (dx / dist) * force
        const fy = (dy / dist) * force
        source.x += fx
        source.y += fy
        target.x -= fx
        target.y -= fy
      }
    }

    return pos
  }, [dimensions, data])

  const containerCallback = useCallback((node: HTMLDivElement | null) => {
    if (node) {
      containerRef.current = node
      const rect = node.getBoundingClientRect()
      setDimensions({ width: rect.width, height: rect.height })
    }
  }, [])

  const zoomIn = () => setScale(s => Math.min(s + 0.1, 2))
  const zoomOut = () => setScale(s => Math.max(s - 0.1, 0.5))
  const resetZoom = () => setScale(1)

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 py-8">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">National Civic Knowledge Graph</h1>
            <p className="text-muted-foreground text-sm mt-1">
              Jelajahi hubungan antara program, instansi, dokumen, dan manfaat
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Cari node..."
                className="pl-9 w-56 h-9 text-sm"
              />
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          {/* Graph */}
          <div className="lg:col-span-3">
            <Card className="overflow-hidden">
              <div className="relative">
                <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/30">
                  <div className="flex items-center gap-2">
                    <Share2 className="h-4 w-4 text-primary" />
                    <span className="text-sm font-medium">Interactive Knowledge Graph</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <button onClick={zoomIn} className="p-1.5 hover:bg-accent rounded transition-colors">
                      <ZoomIn className="h-4 w-4" />
                    </button>
                    <button onClick={zoomOut} className="p-1.5 hover:bg-accent rounded transition-colors">
                      <ZoomOut className="h-4 w-4" />
                    </button>
                    <button onClick={resetZoom} className="p-1.5 hover:bg-accent rounded transition-colors">
                      <RotateCcw className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                <div
                  ref={containerCallback}
                  className="w-full h-[600px] relative overflow-hidden bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/5 via-transparent to-transparent"
                >
                  <svg
                    width={dimensions.width}
                    height={dimensions.height}
                    style={{ transform: `scale(${scale})`, transformOrigin: "center center", transition: "transform 0.2s" }}
                  >
                    {/* Links */}
                    {filteredLinks.map((link) => {
                      const source = positions.get(link.source)
                      const target = positions.get(link.target)
                      if (!source || !target) return null
                      const isHighlighted = hoveredNode === link.source || hoveredNode === link.target
                      return (
                        <g key={`${link.source}-${link.target}`}>
                          <line
                            x1={source.x} y1={source.y}
                            x2={target.x} y2={target.y}
                            stroke={isHighlighted ? "hsl(221.2 83.2% 53.3%)" : "hsl(214.3 31.8% 85%)"}
                            strokeWidth={isHighlighted ? 2 : 1}
                            opacity={hoveredNode && !isHighlighted ? 0.1 : 0.6}
                            className="transition-all duration-200"
                          />
                          <text
                            x={(source.x + target.x) / 2}
                            y={(source.y + target.y) / 2 - 6}
                            textAnchor="middle"
                            className="text-[9px] fill-muted-foreground"
                          >
                            {link.label}
                          </text>
                        </g>
                      )
                    })}

                    {/* Nodes */}
                    {filteredNodes.map((node) => {
                      const pos = positions.get(node.id)
                      if (!pos) return null
                      const isSelected = selectedNode?.id === node.id
                      const isHovered = hoveredNode === node.id
                      const radius = isSelected ? 28 : isHovered ? 24 : 20
                      return (
                        <g
                          key={node.id}
                          transform={`translate(${pos.x}, ${pos.y})`}
                          className="cursor-pointer"
                          onClick={() => setSelectedNode(node)}
                          onMouseEnter={() => setHoveredNode(node.id)}
                          onMouseLeave={() => setHoveredNode(null)}
                        >
                          <circle
                            r={radius}
                            fill={`url(#grad-${node.type})`}
                            stroke={isSelected ? "hsl(221.2 83.2% 53.3%)" : "transparent"}
                            strokeWidth={isSelected ? 3 : 0}
                            className="transition-all duration-200 drop-shadow-md"
                            opacity={hoveredNode && !isHovered && !isSelected ? 0.3 : 1}
                          />
                          <text
                            textAnchor="middle"
                            dy="0.35em"
                            className="fill-white text-[8px] font-medium pointer-events-none"
                          >
                            {node.label.length > 12 ? node.label.slice(0, 11) + '…' : node.label}
                          </text>
                          <foreignObject
                            x={-60}
                            y={radius + 4}
                            width={120}
                            height={18}
                          >
                            <div className="text-[8px] text-center text-muted-foreground leading-tight pointer-events-none">
                              {typeLabels[node.type]}
                            </div>
                          </foreignObject>
                        </g>
                      )
                    })}

                    {/* Defs */}
                    <defs>
                      {Object.entries(typeColors).map(([type]) => (
                        <linearGradient key={type} id={`grad-${type}`} x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor={`oklch(0.7 0.15 ${type === "program" ? "220" : type === "agency" ? "280" : type === "document" ? "70" : type === "benefit" ? "160" : type === "location" ? "0" : "260"})`} />
                          <stop offset="100%" stopColor={`oklch(0.5 0.15 ${type === "program" ? "240" : type === "agency" ? "320" : type === "document" ? "60" : type === "benefit" ? "180" : type === "location" ? "20" : "290"})`} />
                        </linearGradient>
                      ))}
                    </defs>
                  </svg>
                </div>
              </div>
            </Card>
          </div>

          {/* Details Panel */}
          <div className="space-y-4">
            {/* Legend */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Legend</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {Object.entries(typeLabels).map(([type, label]) => (
                  <div key={type} className="flex items-center gap-2 text-sm">
                    <div className={`w-3 h-3 rounded-full bg-gradient-to-br ${typeColors[type]}`} />
                    <span className="text-muted-foreground">{label}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Node Details */}
            {selectedNode ? (
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Info className="h-4 w-4 text-primary" />
                      Detail
                    </CardTitle>
                    <button onClick={() => setSelectedNode(null)} className="p-1 hover:bg-accent rounded transition-colors">
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${typeColors[selectedNode.type]} p-1.5`}>
                    <Share2 className="h-full w-full text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{selectedNode.label}</h3>
                    <Badge variant="secondary" className="text-xs mt-1">{typeLabels[selectedNode.type]}</Badge>
                  </div>
                  {selectedNode.description && (
                    <p className="text-sm text-muted-foreground">{selectedNode.description}</p>
                  )}
                  <div className="pt-2 border-t">
                    <p className="text-xs font-medium text-muted-foreground mb-2">Koneksi ({filteredLinks.filter(l => l.source === selectedNode.id || l.target === selectedNode.id).length})</p>
                    <div className="space-y-1 max-h-32 overflow-y-auto">
                      {filteredLinks
                        .filter(l => l.source === selectedNode.id || l.target === selectedNode.id)
                        .map((link) => {
                          const relatedId = link.source === selectedNode.id ? link.target : link.source
                          const related = data.nodes.find(n => n.id === relatedId)
                          return (
                            <div
                              key={`${link.source}-${link.target}`}
                              className="flex items-center gap-2 p-1.5 rounded hover:bg-muted/50 transition-colors cursor-pointer text-xs"
                              onClick={() => {
                                const r = data.nodes.find(n => n.id === relatedId)
                                if (r) setSelectedNode(r)
                              }}
                            >
                              <div className={`w-2 h-2 rounded-full bg-gradient-to-br ${typeColors[related?.type || "program"]}`} />
                              <span className="text-muted-foreground">{link.label}</span>
                              <span className="font-medium ml-auto">{related?.label}</span>
                            </div>
                          )
                        })}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <Share2 className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">Klik node untuk melihat detail</p>
                </CardContent>
              </Card>
            )}

            {/* Stats */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm">Statistik Graph</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Node</span>
                  <span className="font-medium">{data.nodes.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Koneksi</span>
                  <span className="font-medium">{data.links.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Program</span>
                  <span className="font-medium">{data.nodes.filter(n => n.type === "program").length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Instansi</span>
                  <span className="font-medium">{data.nodes.filter(n => n.type === "agency").length}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
