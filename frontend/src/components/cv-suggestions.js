import css from './cv-suggestions.css?inline'

const styles = new CSSStyleSheet()
styles.replaceSync(css)

class CvSuggestions extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
    this.shadowRoot.adoptedStyleSheets = [styles]
    this._render()
  }

  set suggestions(text) {
    const el = this.shadowRoot.querySelector('.suggestions-content')
    if (el) el.textContent = text || ''
  }

  _render() {
    this.shadowRoot.innerHTML = `
      <details class="suggestions-wrapper">
        <summary>Sugerencias para el CV</summary>
        <div class="suggestions-body">
          <div class="suggestions-content" aria-live="polite"></div>
        </div>
      </details>
    `
  }
}

customElements.define('cv-suggestions', CvSuggestions)
