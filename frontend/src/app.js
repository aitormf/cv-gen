import './components/markdown-editor.js'
import './components/template-selector.js'
import './components/pdf-preview.js'
import { fetchTemplates } from './api.js'

const editor = document.querySelector('markdown-editor')
const selector = document.querySelector('template-selector')
const preview = document.querySelector('pdf-preview')

editor.addEventListener('input', (e) => {
  preview.markdown = e.detail
})

selector.addEventListener('change', (e) => {
  preview.template = e.detail
})

fetchTemplates().then((data) => {
  selector.templates = data.templates
  selector.selected = data.default
  preview.template = data.default
})
