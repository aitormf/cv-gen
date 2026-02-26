import './components/markdown-editor.js'
import './components/template-selector.js'
import './components/pdf-preview.js'
import './components/doc-upload.js'
import { fetchTemplates, checkAiStatus } from './api.js'

const editor = document.querySelector('markdown-editor')
const selector = document.querySelector('template-selector')
const preview = document.querySelector('pdf-preview')
const docUpload = document.querySelector('doc-upload')

editor.addEventListener('input', (e) => {
  preview.markdown = e.detail
})

selector.addEventListener('change', (e) => {
  preview.template = e.detail
})

if (docUpload) {
  docUpload.addEventListener('converted', (e) => {
    editor.value = e.detail
    preview.markdown = e.detail
  })
}

fetchTemplates().then((data) => {
  selector.templates = data.templates
  selector.selected = data.default
  preview.template = data.default
})

checkAiStatus().then((data) => {
  if (docUpload) docUpload.hidden = !data.available
})
