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
