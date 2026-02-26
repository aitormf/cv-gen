import { generatePdf, downloadBlob } from '../api.js'
import css from './pdf-preview.css?inline'

const styles = new CSSStyleSheet()
styles.replaceSync(css)

class PdfPreview extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
    this.shadowRoot.adoptedStyleSheets = [styles]

    this._markdown = ''
    this._template = 'modern'
    this._pdfUrl = ''
    this._isGenerating = false

    this._render()
  }

  get markdown() {
    return this._markdown
  }

  set markdown(v) {
    this._markdown = v
    this._updateGenerateBtn()
  }

  get template() {
    return this._template
  }

  set template(v) {
    this._template = v
  }

  _render() {
    this.shadowRoot.innerHTML = `
      <div class="preview-wrapper">
        <div class="empty">
          <p>Escribe tu CV en Markdown y pulsa <strong>Generar PDF</strong></p>
        </div>
        <div class="actions">
          <button class="generate-btn" disabled>Generar PDF</button>
        </div>
      </div>
    `

    this._wrapper = this.shadowRoot.querySelector('.preview-wrapper')
    this._emptyEl = this.shadowRoot.querySelector('.empty')
    this._actionsEl = this.shadowRoot.querySelector('.actions')
    this._generateBtn = this.shadowRoot.querySelector('.generate-btn')

    this._generateBtn.addEventListener('click', () => this._handleGenerate())
  }

  _updateGenerateBtn() {
    this._generateBtn.disabled = this._isGenerating || !this._markdown.trim()
  }

  async _handleGenerate() {
    if (!this._markdown.trim()) return
    this._isGenerating = true
    this._generateBtn.disabled = true
    this._generateBtn.textContent = 'Generando...'

    try {
      if (this._pdfUrl) URL.revokeObjectURL(this._pdfUrl)
      this._pdfUrl = await generatePdf(this._markdown, this._template)
      this._showPdf()
    } finally {
      this._isGenerating = false
      this._generateBtn.textContent = 'Generar PDF'
      this._updateGenerateBtn()
    }
  }

  _showPdf() {
    if (this._emptyEl) {
      this._emptyEl.remove()
      this._emptyEl = null
    }

    let iframe = this.shadowRoot.querySelector('iframe')
    if (!iframe) {
      iframe = document.createElement('iframe')
      iframe.title = 'CV Preview'
      this._wrapper.insertBefore(iframe, this._actionsEl)
    }
    iframe.src = this._pdfUrl

    let downloadBtn = this.shadowRoot.querySelector('.download-btn')
    if (!downloadBtn) {
      downloadBtn = document.createElement('button')
      downloadBtn.className = 'download-btn'
      downloadBtn.textContent = 'Descargar PDF'
      downloadBtn.addEventListener('click', () => this._handleDownload())
      this._actionsEl.appendChild(downloadBtn)
    }
  }

  _handleDownload() {
    if (this._pdfUrl) downloadBlob(this._pdfUrl, 'cv.pdf')
  }
}

customElements.define('pdf-preview', PdfPreview)
