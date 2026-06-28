import { CopilotResponse, KnowledgeGraphData, AnalyticsData, ActionPlanResponse, PolicySimulationResponse, HoaxCheckResponse } from './api'

export const mockCopilotResponse: CopilotResponse = {
  session_id: 'sess_' + Math.random().toString(36).slice(2),
  type: "analysis",
  response: {
    summary: 'Berdasarkan situasi yang Anda sampaikan, kami mengidentifikasi bahwa Anda memerlukan bantuan untuk mengurus dokumen kependudukan dan mengakses program bantuan sosial pendidikan.',
    analysis: 'Dari informasi yang diberikan, Anda berada dalam kategori warga yang berpotensi memperoleh bantuan dari beberapa program pemerintah. Kami merekomendasikan prioritas pada pengurusan dokumen dasar terlebih dahulu.',
    relevant_programs: [
      {
        name: 'Program Indonesia Pintar (PIP)',
        agency: 'Kemdikdasmen',
        description: 'Bantuan pendidikan untuk anak usia sekolah dari keluarga miskin/rentan',
        match_score: 92,
        url: 'https://pip.kemdikbud.go.id',
      },
      {
        name: 'Kartu Indonesia Sehat (KIS)',
        agency: 'BPJS Kesehatan',
        description: 'Jaminan kesehatan bagi masyarakat kurang mampu',
        match_score: 85,
      },
      {
        name: 'Bantuan Pangan Non-Tunai (BPNT)',
        agency: 'Kemensos',
        description: 'Bantuan pangan untuk keluarga kurang mampu',
        match_score: 78,
      },
    ],
    required_documents: [
      { name: 'Kartu Keluarga (KK)', description: 'KK asli dan fotokopi 3 lembar', priority: 'high' },
      { name: 'KTP Elektronik', description: 'KTP-el asli dan fotokopi 3 lembar', priority: 'high' },
      { name: 'Akta Kelahiran', description: 'Akta kelahiran anak (jika ada)', priority: 'medium' },
      { name: 'Surat Keterangan Tidak Mampu (SKTM)', description: 'Dari kelurahan/desa setempat', priority: 'medium' },
      { name: 'Rapor/SKHUN', description: 'Untuk program pendidikan', priority: 'low' },
    ],
    risk_factors: [
      { risk: 'Dokumen KK tidak terdaftar di Dukcapil', severity: 'high', mitigation: 'Segera cek status KK di Dukcapil online atau datang ke kantor Dukcapil' },
      { risk: 'Perubahan status ekonomi mempengaruhi eligibilitas', severity: 'medium', mitigation: 'Siapkan dokumen pendukung kondisi ekonomi terkini' },
      { risk: 'Batas waktu pendaftaran program', severity: 'low', mitigation: 'Cek jadwal pendaftaran program di website resmi' },
    ],
    timeline: {
      estimated_days: 14,
      steps: [
        { step: 1, action: 'Verifikasi dokumen kependudukan', duration: '1-2 hari', office: 'Dukcapil' },
        { step: 2, action: 'Urus SKTM ke kelurahan', duration: '1 hari', office: 'Kantor Kelurahan' },
        { step: 3, action: 'Daftar PIP secara online/offline', duration: '3-5 hari', office: 'Sekolah/Dinas Pendidikan' },
        { step: 4, action: 'Aktivasi rekening bantuan', duration: '2-3 hari', office: 'Bank Penyalur' },
        { step: 5, action: 'Konfirmasi penerimaan bantuan', duration: '1-2 hari', office: '-' },
      ],
    },
    action_plan: {
      today: ['Kumpulkan KK dan KTP', 'Hubungi kelurahan untuk SKTM', 'Cek jadwal pendaftaran PIP'],
      this_week: ['Verifikasi dokumen ke Dukcapil', 'Ambil SKTM di kelurahan', 'Daftar program PIP'],
      next_step: ['Aktivasi rekening bantuan', 'Pantau status penerimaan'],
    },
    success_probability: 78,
    trust_score: {
      overall: 92,
      reliability: 95,
      freshness: 88,
      verification: 90,
      transparency: 94,
    },
    sources: [
      { title: 'Portal PIP - Kemdikdasmen', url: 'https://pip.kemdikbud.go.id', type: 'government' },
      { title: 'Data Terpadu Kesejahteraan Sosial (DTKS)', url: 'https://dtks.kemensos.go.id', type: 'government' },
      { title: 'Kemendagri - Dukcapil', url: 'https://dukcapil.kemendagri.go.id', type: 'government' },
    ],
  },
}

export const mockKnowledgeGraphData: KnowledgeGraphData = {
  nodes: [
    { id: 'pip', label: 'Program Indonesia Pintar', type: 'program', description: 'Bantuan pendidikan untuk siswa kurang mampu' },
    { id: 'kip', label: 'Kartu Indonesia Pintar', type: 'program', description: 'Kartu identitas penerima PIP' },
    { id: 'kis', label: 'Kartu Indonesia Sehat', type: 'program', description: 'Jaminan kesehatan masyarakat' },
    { id: 'bpnt', label: 'Bantuan Pangan Non-Tunai', type: 'program', description: 'Bantuan pangan untuk keluarga miskin' },
    { id: 'pkh', label: 'Program Keluarga Harapan', type: 'program', description: 'Bantuan sosial bersyarat' },
    { id: 'kemendikdasmen', label: 'Kemdikdasmen', type: 'agency', description: 'Kementerian Pendidikan Dasar dan Menengah' },
    { id: 'kemensos', label: 'Kemensos RI', type: 'agency', description: 'Kementerian Sosial RI' },
    { id: 'bpjs', label: 'BPJS Kesehatan', type: 'agency', description: 'Badan Penyelenggara Jaminan Sosial' },
    { id: 'dukcapil', label: 'Ditjen Dukcapil', type: 'agency', description: 'Direktorat Jenderal Kependudukan dan Pencatatan Sipil' },
    { id: 'kk', label: 'Kartu Keluarga', type: 'document', description: 'Dokumen identitas keluarga' },
    { id: 'ktp', label: 'KTP Elektronik', type: 'document', description: 'Kartu Tanda Penduduk elektronik' },
    { id: 'akte', label: 'Akta Kelahiran', type: 'document', description: 'Dokumen kelahiran' },
    { id: 'sktm', label: 'SKTM', type: 'document', description: 'Surat Keterangan Tidak Mampu' },
    { id: 'bantuan_pendidikan', label: 'Bantuan Pendidikan', type: 'benefit', description: 'Dana bantuan untuk biaya pendidikan' },
    { id: 'bantuan_kesehatan', label: 'Bantuan Kesehatan', type: 'benefit', description: 'Akses layanan kesehatan gratis' },
    { id: 'bantuan_pangan', label: 'Bantuan Pangan', type: 'benefit', description: 'Bantuan kebutuhan pangan' },
    { id: 'kantor_kelurahan', label: 'Kantor Kelurahan', type: 'location', description: 'Kantor pelayanan kelurahan' },
    { id: 'kecamatan', label: 'Kantor Kecamatan', type: 'location', description: 'Kantor pelayanan kecamatan' },
    { id: 'dtks', label: 'DTKS', type: 'requirement', description: 'Terdaftar di Data Terpadu Kesejahteraan Sosial' },
    { id: 'nik', label: 'Memiliki NIK', type: 'requirement', description: 'Nomor Induk Kependudukan valid' },
  ],
  links: [
    { source: 'pip', target: 'kemendikdasmen', label: 'dikelola oleh' },
    { source: 'kip', target: 'pip', label: 'bagian dari' },
    { source: 'pip', target: 'bantuan_pendidikan', label: 'memberikan' },
    { source: 'kis', target: 'bpjs', label: 'dikelola oleh' },
    { source: 'kis', target: 'bantuan_kesehatan', label: 'memberikan' },
    { source: 'bpnt', target: 'kemensos', label: 'dikelola oleh' },
    { source: 'bpnt', target: 'bantuan_pangan', label: 'memberikan' },
    { source: 'pkh', target: 'kemensos', label: 'dikelola oleh' },
    { source: 'pkh', target: 'bantuan_pendidikan', label: 'memberikan' },
    { source: 'pkh', target: 'bantuan_kesehatan', label: 'memberikan' },
    { source: 'kk', target: 'dukcapil', label: 'diterbitkan oleh' },
    { source: 'ktp', target: 'dukcapil', label: 'diterbitkan oleh' },
    { source: 'akte', target: 'dukcapil', label: 'diterbitkan oleh' },
    { source: 'sktm', target: 'kantor_kelurahan', label: 'diterbitkan oleh' },
    { source: 'pip', target: 'kk', label: 'membutuhkan' },
    { source: 'pip', target: 'ktp', label: 'membutuhkan' },
    { source: 'pip', target: 'sktm', label: 'membutuhkan' },
    { source: 'pip', target: 'dtks', label: 'memerlukan' },
    { source: 'pip', target: 'nik', label: 'memerlukan' },
    { source: 'kis', target: 'kk', label: 'membutuhkan' },
    { source: 'kis', target: 'nik', label: 'memerlukan' },
    { source: 'bpnt', target: 'kk', label: 'membutuhkan' },
    { source: 'bpnt', target: 'ktp', label: 'membutuhkan' },
    { source: 'pkh', target: 'dtks', label: 'memerlukan' },
    { source: 'pkh', target: 'kk', label: 'membutuhkan' },
    { source: 'kemendikdasmen', target: 'kecamatan', label: 'memiliki kantor di' },
    { source: 'kemensos', target: 'kantor_kelurahan', label: 'bekerja sama dengan' },
    { source: 'pip', target: 'kis', label: 'terkait' },
    { source: 'pkh', target: 'bpnt', label: 'dapat digabung dengan' },
  ],
}

export const mockAnalyticsData: AnalyticsData = {
  total_citizens_served: 124583,
  total_time_saved_minutes: 4890000,
  total_programs_discovered: 15420,
  total_procedures_simplified: 892,
  estimated_economic_impact: 15780000000,
  average_trust_score: 87,
  average_success_score: 76,
  community_trends: [
    { category: 'Pendidikan', change: 23, direction: 'up', period: 'Bulan ini' },
    { category: 'Kesehatan', change: 15, direction: 'up', period: 'Bulan ini' },
    { category: 'Bantuan Sosial', change: 31, direction: 'up', period: 'Bulan ini' },
    { category: 'Ketenagakerjaan', change: 8, direction: 'down', period: 'Bulan ini' },
  ],
  top_concerns: [
    { issue: 'Pendaftaran PIP', count: 4521, growth: 34 },
    { issue: 'Pengurusan KK', count: 3890, growth: 18 },
    { issue: 'BPJS Kesehatan', count: 3102, growth: 22 },
    { issue: 'Bansos Tunai', count: 2890, growth: 45 },
    { issue: 'SKTM', count: 2100, growth: 12 },
  ],
  regional_scores: {
    'Jakarta': { education: 82, health: 78, social: 71, accessibility: 85 },
    'Jawa Barat': { education: 74, health: 69, social: 65, accessibility: 72 },
    'Jawa Timur': { education: 76, health: 71, social: 68, accessibility: 70 },
    'Jawa Tengah': { education: 78, health: 73, social: 70, accessibility: 74 },
    'Sumatera Utara': { education: 68, health: 65, social: 62, accessibility: 64 },
    'Sulawesi Selatan': { education: 72, health: 68, social: 64, accessibility: 66 },
    'Papua': { education: 45, health: 42, social: 38, accessibility: 35 },
    'Nusa Tenggara Timur': { education: 52, health: 48, social: 44, accessibility: 42 },
  },
}

export function generateMockActionPlan(situation: string): ActionPlanResponse {
  return {
    title: 'Rencana Aksi: ' + situation.split('.').slice(0, 1)[0],
    overview: 'Berdasarkan situasi yang Anda alami, JERNIH OS telah menganalisis kebutuhan dan menyusun rencana aksi personal untuk membantu Anda mengurus dokumen dan mengakses program bantuan yang sesuai.',
    citizen_success_score: 82,
    document_readiness: 65,
    eligibility_score: 78,
    program_match: 91,
    timeline: [
      {
        phase: 'Hari Ini',
        tasks: [
          { task: 'Kumpulkan dokumen KK dan KTP', deadline: 'Hari ini', priority: 'high', done: false },
          { task: 'Hubungi RT/RW untuk surat pengantar', deadline: 'Hari ini', priority: 'high', done: false },
          { task: 'Cek persyaratan program di website resmi', deadline: 'Hari ini', priority: 'medium', done: false },
        ],
      },
      {
        phase: 'Minggu Ini',
        tasks: [
          { task: 'Ambil SKTM di Kantor Kelurahan', deadline: '3 hari', priority: 'high', done: false },
          { task: 'Verifikasi dokumen ke Dukcapil', deadline: '5 hari', priority: 'high', done: false },
          { task: 'Daftar program PIP/KIP', deadline: '7 hari', priority: 'high', done: false },
        ],
      },
      {
        phase: 'Minggu Depan',
        tasks: [
          { task: 'Pantau status pendaftaran', deadline: '14 hari', priority: 'medium', done: false },
          { task: 'Aktivasi rekening bantuan', deadline: '14 hari', priority: 'medium', done: false },
        ],
      },
    ],
    required_documents: [
      { name: 'Kartu Keluarga (KK)', status: 'need', notes: 'Fotokopi 3 lembar' },
      { name: 'KTP Elektronik', status: 'ready' },
      { name: 'Akta Kelahiran', status: 'optional', notes: 'Jika tersedia' },
      { name: 'SKTM', status: 'need', notes: 'Ambil di kelurahan' },
      { name: 'Pas Foto 3x4', status: 'need', notes: '4 lembar background merah' },
    ],
    recommendations: [
      'Segera urus dokumen kependudukan jika belum lengkap',
      'Daftar DTKS untuk memperkuat eligibilitas bantuan',
      'Cek jadwal pendaftaran PIP yang biasanya dibuka 2 kali setahun',
      'Siapkan dokumen pendukung tambahan untuk mempercepat proses',
      'Manfaatkan layanan pengaduan jika ada kendala di lapangan',
    ],
    risks: [
      { risk: 'Dokumen KK tidak update', probability: 'medium', impact: 'high' },
      { risk: 'Antrean panjang di kelurahan', probability: 'high', impact: 'medium' },
      { risk: 'Kuota program terbatas', probability: 'medium', impact: 'high' },
    ],
  }
}

export function generateMockPolicySimulation(policy: string, change: string): PolicySimulationResponse {
  return {
    summary: `Simulasi perubahan kebijakan ${policy}: "${change}" menunjukkan dampak signifikan terhadap cakupan penerima manfaat.`,
    affected_groups: [
      { group: 'Siswa SMA/SMK dari keluarga miskin', impact: 'positive', estimate: '+45,000 penerima baru' },
      { group: 'Mahasiswa rantau', impact: 'positive', estimate: '+12,000 penerima baru' },
      { group: 'Penerima manfaat eksisting', impact: 'neutral', estimate: 'Tidak ada perubahan' },
      { group: 'Masyarakat berpendapatan menengah', impact: 'negative', estimate: '-8,000 kehilangan akses' },
    ],
    coverage_change: {
      before: 8900000,
      after: 9450000,
      difference: 550000,
    },
    opportunity_loss: 'Diperkirakan 8,000 warga dari kelompok menengah kehilangan akses, namun 550,000 warga baru dari kelompok rentan mendapatkan akses. Dampak bersih: positif.',
    social_impact: 'Perubahan ini berpotensi meningkatkan angka partisipasi sekolah menengah hingga 3.2% dan mengurangi angka putus sekolah akibat ekonomi.',
    recommendations: [
      'Sosialisasikan perubahan kebijakan secara masif',
      'Siapkan jalur pengaduan bagi warga yang terdampak negatif',
      'Alokasikan dana transisi untuk penerima yang kehilangan akses',
      'Monitoring dampak selama 6 bulan pertama implementasi',
    ],
  }
}

export function generateMockHoaxCheck(): HoaxCheckResponse {
  return {
    credibility_score: 23,
    verdict: 'hoax',
    analysis: 'Informasi ini memiliki indikasi kuat sebagai hoaks. Kami menemukan beberapa perbedaan signifikan dengan data resmi pemerintah. Sebarkan informasi yang benar dan verifikasi ke sumber terpercaya.',
    source_comparison: [
      { source: 'Portal Informasi Indonesia (data.go.id)', alignment: 'contradicts', excerpt: 'Data resmi menunjukkan tidak ada kebijakan tersebut' },
      { source: 'Kemensos RI', alignment: 'contradicts', excerpt: 'Tidak ditemukan program dengan nama tersebut' },
      { source: 'FactCheck.id', alignment: 'contradicts', excerpt: 'Informasi serupa telah difaktualisasi sebagai hoaks' },
      { source: 'WhatsApp Group', alignment: 'supports', excerpt: 'Pesan berantai tidak terverifikasi' },
    ],
    fact_checks: [
      { claim: 'Pemerintah membagikan bantuan Rp2,5 juta', verdict: 'SALAH', source: 'Kemensos RI' },
      { claim: 'Cukup daftar via link untuk mendapatkan dana', verdict: 'SALAH', source: 'Kominfo' },
      { claim: 'Tidak perlu verifikasi data', verdict: 'SALAH', source: 'Portal Anti Hoax' },
    ],
    indicators: [
      'Menggunakan domain tidak resmi (.xyz, .info, dll)',
      'Meminta data pribadi secara berlebihan',
      'Klaim dana besar dengan syarat mudah',
      'Informasi tidak ditemukan di website resmi',
      'Menggunakan bahasa yang mendesak/menakut-nakuti',
    ],
  }
}
