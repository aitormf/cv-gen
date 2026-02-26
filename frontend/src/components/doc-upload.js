import { convertDocument } from '../api.js'
import css from './doc-upload.css?inline'

const styles = new CSSStyleSheet()
styles.replaceSync(css)

class DocUpload extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
    this.shadowRoot.adoptedStyleSheets = [styles]

    this._input = document.createElement('input')
    this._input.type = 'file'
    this._input.accept = '.pdf,.docx'
    this._input.hidden = true

    this._btn = document.createElement('button')
    this._btn.className = 'upload-btn'
    this._btn.textContent = 'Importar CV'

    this.shadowRoot.append(this._input, this._btn)

    this._btn.addEventListener('click', () => this._input.click())
    this._input.addEventListener('change', () => this._handleFile())
  }

  async _handleFile() {
    const file = this._input.files[0]
    if (!file) return

    this._btn.disabled = true
    this._btn.textContent = 'Convirtiendo...'
    this._btn.className = 'upload-btn upload-btn--converting'

    try {
      const markdown = await convertDocument(file)
      this._btn.textContent = 'Importar CV'
      this._btn.className = 'upload-btn'
      this.dispatchEvent(new CustomEvent('converted', { detail: markdown }))
    } catch (err) {
      this._btn.textContent = 'Error - Reintentar'
      this._btn.className = 'upload-btn upload-btn--error'
    } finally {
      this._btn.disabled = false
      this._input.value = ''
    }
  }
}

customElements.define('doc-upload', DocUpload)
