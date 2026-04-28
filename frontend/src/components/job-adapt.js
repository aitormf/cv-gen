import { adaptCV } from '../api.js'
import css from './job-adapt.css?inline'

const styles = new CSSStyleSheet()
styles.replaceSync(css)

class JobAdapt extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
    this.shadowRoot.adoptedStyleSheets = [styles]

    this._baseMarkdown = ''
    this._isAdapting = false

    this._render()
  }

  get baseMarkdown() {
    return this._baseMarkdown
  }

  set baseMarkdown(v) {
    this._baseMarkdown = v
    this._updateBtn()
  }

  _render() {
    this.shadowRoot.innerHTML = `
      <details class="adapt-wrapper">
        <summary>Adaptar a oferta de trabajo</summary>
        <div class="adapt-body">
          <textarea placeholder="Pega aquí el texto de la oferta de empleo..."></textarea>
          <button class="adapt-btn" disabled>Adaptar CV</button>
          <span class="error" hidden></span>
        </div>
      </details>
    `

    this._textarea = this.shadowRoot.querySelector('textarea')
    this._btn = this.shadowRoot.querySelector('.adapt-btn')
    this._errorEl = this.shadowRoot.querySelector('.error')

    this._textarea.addEventListener('input', () => this._updateBtn())
    this._btn.addEventListener('click', () => this._handleAdapt())
  }

  _updateBtn() {
    this._btn.disabled =
      this._isAdapting ||
      !this._baseMarkdown.trim() ||
      !this._textarea.value.trim()
  }

  async _handleAdapt() {
    const jobOffer = this._textarea.value.trim()
    if (!this._baseMarkdown.trim() || !jobOffer) return

    this._isAdapting = true
    this._btn.disabled = true
    this._btn.textContent = 'Adaptando...'
    this._errorEl.hidden = true

    try {
      const result = await adaptCV(this._baseMarkdown, jobOffer)
      this.dispatchEvent(new CustomEvent('cv-adapted', { detail: result, bubbles: true }))
    } catch (err) {
      this._errorEl.textContent = err.message || 'Error al adaptar el CV'
      this._errorEl.hidden = false
    } finally {
      this._isAdapting = false
      this._btn.textContent = 'Adaptar CV'
      this._updateBtn()
    }
  }
}

customElements.define('job-adapt', JobAdapt)
