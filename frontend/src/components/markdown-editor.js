import css from './markdown-editor.css?inline'

const styles = new CSSStyleSheet()
styles.replaceSync(css)

const PLACEHOLDER = `---
name: Your Name
title: Software Engineer
email: you@example.com
---

## Experience

**Company** | Role | 2020 - Present

- Did amazing things`

class MarkdownEditor extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
    this.shadowRoot.adoptedStyleSheets = [styles]

    this._textarea = document.createElement('textarea')
    this._textarea.spellcheck = false
    this._textarea.placeholder = PLACEHOLDER
    this.shadowRoot.appendChild(this._textarea)

    this._textarea.addEventListener('input', (e) => {
      e.stopPropagation()
      this.dispatchEvent(new CustomEvent('input', { detail: this._textarea.value }))
    })
  }

  get value() {
    return this._textarea.value
  }

  set value(v) {
    this._textarea.value = v
  }
}

customElements.define('markdown-editor', MarkdownEditor)
