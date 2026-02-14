<script lang="ts">
  import { generatePdf, downloadBlob } from "../lib/api";

  interface Props {
    markdown: string;
    template: string;
  }

  let { markdown, template }: Props = $props();
  let pdfUrl = $state("");
  let isGenerating = $state(false);

  async function handleGenerate() {
    if (!markdown.trim()) return;
    isGenerating = true;
    try {
      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
      pdfUrl = await generatePdf(markdown, template);
    } finally {
      isGenerating = false;
    }
  }

  function handleDownload() {
    if (pdfUrl) downloadBlob(pdfUrl, "cv.pdf");
  }
</script>

<div class="preview-wrapper">
  {#if pdfUrl}
    <iframe src={pdfUrl} title="CV Preview"></iframe>
  {:else}
    <div class="empty">
      <p>Escribe tu CV en Markdown y pulsa <strong>Generar PDF</strong></p>
    </div>
  {/if}

  <div class="actions">
    <button class="generate-btn" onclick={handleGenerate} disabled={isGenerating || !markdown.trim()}>
      {isGenerating ? "Generando..." : "Generar PDF"}
    </button>
    {#if pdfUrl}
      <button class="download-btn" onclick={handleDownload}>
        Descargar PDF
      </button>
    {/if}
  </div>
</div>

<style>
  .preview-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  iframe {
    flex: 1;
    width: 100%;
    border: none;
    background: #585b70;
  }

  .empty {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6c7086;
    font-size: 0.9rem;
    text-align: center;
    padding: 2rem;
  }

  .actions {
    display: flex;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: #181825;
    border-top: 1px solid #313244;
  }

  .generate-btn,
  .download-btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.8rem;
    cursor: pointer;
    transition: background 0.15s;
  }

  .generate-btn {
    background: #89b4fa;
    color: #1e1e2e;
  }

  .generate-btn:hover:not(:disabled) {
    background: #74c7ec;
  }

  .generate-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .download-btn {
    background: #a6e3a1;
    color: #1e1e2e;
  }

  .download-btn:hover {
    background: #94e2d5;
  }
</style>
