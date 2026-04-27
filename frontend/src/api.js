export async function fetchTemplates() {
  const res = await fetch('/api/templates')
  if (!res.ok) throw new Error(`Failed to fetch templates: ${res.status}`)
  return res.json()
}

export async function generatePdf(markdown, template) {
  const res = await fetch('/api/pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ markdown, template }),
  })
  if (!res.ok) throw new Error(`Failed to generate PDF: ${res.status}`)
  const blob = await res.blob()
  return URL.createObjectURL(blob)
}

export function downloadBlob(url, filename) {
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
}

export async function checkAiStatus() {
  const res = await fetch('/api/ai/status')
  if (!res.ok) return { available: false }
  return res.json()
}

export async function adaptCV(markdown, jobOffer) {
  const res = await fetch('/api/ai/adapt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ markdown, job_offer: jobOffer }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || `Adaptation failed: ${res.status}`)
  }
  const data = await res.json()
  return data.markdown
}

export async function convertDocument(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch('/api/ai/convert', { method: 'POST', body: form })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || `Conversion failed: ${res.status}`)
  }
  const data = await res.json()
  return data.markdown
}
