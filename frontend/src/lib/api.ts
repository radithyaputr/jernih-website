const API_BASE = 'https://jernih-project-production.up.railway.app'

export interface CopilotRequest {
  message: string
  session_id?: string
}

// Response shape for analysis/civic queries
export interface CopilotAnalysisResponse {
  session_id: string
  type: "analysis"
  response: {
    summary: string
    analysis: string
    relevant_programs: Array<{
      name: string
      agency: string
      description: string
      match_score: number
      url?: string
    }>
    required_documents: Array<{
      name: string
      description: string
      priority: 'high' | 'medium' | 'low'
    }>
    risk_factors: Array<{
      risk: string
      severity: 'high' | 'medium' | 'low'
      mitigation: string
    }>
    timeline: {
      estimated_days: number
      steps: Array<{
        step: number
        action: string
        duration: string
        office?: string
      }>
    }
    action_plan: {
      today: string[]
      this_week: string[]
      next_step: string[]
    }
    success_probability: number
    trust_score: {
      overall: number
      reliability: number
      freshness: number
      verification: number
      transparency: number
    }
    sources: Array<{
      title: string
      url: string
      type: string
    }>
  }
}

// Response shape for casual/greeting messages
export interface CopilotCasualResponse {
  session_id: string
  type: "casual"
  message: string
}

// Union type — the API can return either
export type CopilotAnyResponse = CopilotAnalysisResponse | CopilotCasualResponse

// Keep backward compat alias for components that only deal with analysis data
export type CopilotResponse = CopilotAnalysisResponse

export interface KnowledgeGraphData {
  nodes: Array<{
    id: string
    label: string
    type: 'program' | 'agency' | 'document' | 'benefit' | 'location' | 'requirement'
    description?: string
  }>
  links: Array<{
    source: string
    target: string
    label: string
  }>
}

export interface AnalyticsData {
  total_citizens_served: number
  total_time_saved_minutes: number
  total_programs_discovered: number
  total_procedures_simplified: number
  estimated_economic_impact: number
  average_trust_score: number
  average_success_score: number
  community_trends: Array<{
    category: string
    change: number
    direction: 'up' | 'down'
    period: string
  }>
  top_concerns: Array<{
    issue: string
    count: number
    growth: number
  }>
  regional_scores: Record<string, {
    education: number
    health: number
    social: number
    accessibility: number
  }>
}

export interface ActionPlanRequest {
  situation: string
}

export interface ActionPlanResponse {
  title: string
  overview: string
  citizen_success_score: number
  document_readiness: number
  eligibility_score: number
  program_match: number
  timeline: Array<{
    phase: string
    tasks: Array<{
      task: string
      deadline: string
      priority: 'high' | 'medium' | 'low'
      done: boolean
    }>
  }>
  required_documents: Array<{
    name: string
    status: 'ready' | 'need' | 'optional'
    notes?: string
  }>
  recommendations: string[]
  risks: Array<{
    risk: string
    probability: 'high' | 'medium' | 'low'
    impact: 'high' | 'medium' | 'low'
  }>
}

export interface PolicySimulationRequest {
  policy: string
  change: string
}

export interface PolicySimulationResponse {
  summary: string
  affected_groups: Array<{
    group: string
    impact: 'positive' | 'negative' | 'neutral'
    estimate: string
  }>
  coverage_change: {
    before: number
    after: number
    difference: number
  }
  opportunity_loss: string
  social_impact: string
  recommendations: string[]
}

export interface HoaxCheckRequest {
  text: string
  type: 'text' | 'url' | 'news'
}

export interface HoaxCheckResponse {
  credibility_score: number
  verdict: 'credible' | 'questionable' | 'hoax'
  analysis: string
  source_comparison: Array<{
    source: string
    alignment: 'supports' | 'contradicts' | 'neutral'
    excerpt?: string
  }>
  fact_checks: Array<{
    claim: string
    verdict: string
    source: string
  }>
  indicators: string[]
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`
  console.log("Fetching from:", url)
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  console.log("Response status:", res.status)
  if (!res.ok) {
    const err = await res.text()
    console.error("API error:", err)
    throw new Error(err || `API error: ${res.status}`)
  }
  const data = await res.json()
  console.log("Response data:", data)
  return data
}

export const api = {
  copilot: {
    chat: (data: CopilotRequest) =>
      fetchAPI<CopilotAnyResponse>('/api/copilot/chat', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  knowledgeGraph: {
    get: () => fetchAPI<KnowledgeGraphData>('/api/knowledge-graph'),
    search: (q: string) => fetchAPI<KnowledgeGraphData>(`/api/knowledge-graph?q=${encodeURIComponent(q)}`),
  },
  analytics: {
    get: () => fetchAPI<AnalyticsData>('/api/analytics'),
  },
  actionPlan: {
    generate: (data: ActionPlanRequest) =>
      fetchAPI<ActionPlanResponse>('/api/action-plan', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  policySimulator: {
    simulate: (data: PolicySimulationRequest) =>
      fetchAPI<PolicySimulationResponse>('/api/policy-simulator', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
  hoaxChecker: {
    check: (data: HoaxCheckRequest) =>
      fetchAPI<HoaxCheckResponse>('/api/hoax-checker', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
}
