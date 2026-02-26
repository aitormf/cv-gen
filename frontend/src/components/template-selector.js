import css from './template-selector.css?inline'

const styles = new CSSStyleSheet()
styles.replaceSync(css)

class TemplateSelector extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
    this.shadowRoot.adoptedStyleSheets = [styles]

    this._select = document.createElement('select')
    this.shadowRoot.appendChild(this._select)

    this._select.addEventListener('change', () => {
      this.dispatchEvent(new CustomEvent('change', { detail: this._select.value }))
    })
  }

  get templates() {
    return [...this._select.options].map((o) => o.value)
  }

  set templates(list) {
    this._select.innerHTML = ''
    for (const t of list) {
      const opt = document.createElement('option')
      opt.value = t
      opt.textContent = t
      this._select.appendChild(opt)
    }
  }

  get selected() {
    return this._select.value
  }

  set selected(v) {
    this._select.value = v
  }
}

customElements.define('template-selector', TemplateSelector)
