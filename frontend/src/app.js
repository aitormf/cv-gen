import './components/markdown-editor.js'
import './components/template-selector.js'
import './components/pdf-preview.js'
import './components/doc-upload.js'
import './components/job-adapt.js'
import './components/cv-suggestions.js'
import { fetchTemplates, checkAiStatus } from './api.js'

const editor = document.querySelector('markdown-editor')
const selector = document.querySelector('template-selector')
const preview = document.querySelector('pdf-preview')
const docUpload = document.querySelector('doc-upload')
const jobAdapt = document.querySelector('job-adapt')

const cvSuggestions = document.querySelector('cv-suggestions')
const editorTabs = document.querySelector('.editor-tabs')
const originalPanel = document.querySelector('.editor-panel--original')
const adaptedPanel = document.querySelector('.editor-panel--adapted')
const adaptedTextarea = document.querySelector('.adapted-markdown-editor')

let activeTab = 'original'

function switchTab(tab) {
  activeTab = tab
  editorTabs.querySelectorAll('.tab-btn').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.tab === tab)
  })
  originalPanel.hidden = tab !== 'original'
  adaptedPanel.hidden = tab !== 'adapted'

  // Sync preview with the active tab's markdown
  preview.markdown = tab === 'original' ? editor.value : adaptedTextarea.value
}

editorTabs.querySelectorAll('.tab-btn').forEach((btn) => {
  btn.addEventListener('click', () => switchTab(btn.dataset.tab))
})

// Base editor changes
editor.addEventListener('input', (e) => {
  if (jobAdapt) jobAdapt.baseMarkdown = e.detail
  if (activeTab === 'original') preview.markdown = e.detail
})

// Template changes
selector.addEventListener('change', (e) => {
  preview.template = e.detail
})

// Doc import
if (docUpload) {
  docUpload.addEventListener('converted', (e) => {
    editor.value = e.detail
    if (jobAdapt) jobAdapt.baseMarkdown = e.detail
    if (activeTab === 'original') preview.markdown = e.detail
  })
}

// CV adaptation result (detail = { markdown, suggestions })
if (jobAdapt) {
  jobAdapt.addEventListener('cv-adapted', (e) => {
    const { markdown, suggestions } = e.detail
    adaptedTextarea.value = markdown
    editorTabs.hidden = false
    switchTab('adapted')
    if (cvSuggestions) cvSuggestions.suggestions = suggestions
  })
}

// Edits in the adapted textarea propagate to preview
adaptedTextarea.addEventListener('input', () => {
  if (activeTab === 'adapted') preview.markdown = adaptedTextarea.value
})

fetchTemplates().then((data) => {
  selector.templates = data.templates
  selector.selected = data.default
  preview.template = data.default
})

checkAiStatus().then((data) => {
  if (docUpload) docUpload.hidden = !data.available
  if (jobAdapt) jobAdapt.hidden = !data.available
})
