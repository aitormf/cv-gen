<script lang="ts">
  import { onMount } from "svelte";
  import { fetchTemplates } from "./lib/api";
  import MarkdownEditor from "./components/MarkdownEditor.svelte";
  import TemplateSelector from "./components/TemplateSelector.svelte";
  import Preview from "./components/Preview.svelte";

  let markdown = $state("");
  let template = $state("modern");
  let templates = $state<string[]>([]);

  onMount(async () => {
    const data = await fetchTemplates();
    templates = data.templates;
    template = data.default;
  });
</script>

<div class="app">
  <header>
    <h1>cv-gen</h1>
    <TemplateSelector {templates} bind:selected={template} />
  </header>

  <div class="panels">
    <section class="editor">
      <MarkdownEditor bind:value={markdown} />
    </section>

    <section class="preview">
      <Preview {markdown} {template} />
    </section>
  </div>
</div>

<style>
  :global(*) {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  :global(body) {
    font-family: system-ui, -apple-system, sans-serif;
    background: #1e1e2e;
    color: #cdd6f4;
  }

  .app {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.5rem;
    background: #181825;
    border-bottom: 1px solid #313244;
  }

  h1 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #89b4fa;
  }

  .panels {
    display: grid;
    grid-template-columns: 1fr 1fr;
    flex: 1;
    overflow: hidden;
  }

  .editor {
    border-right: 1px solid #313244;
    overflow: auto;
  }

  .preview {
    overflow: hidden;
  }
</style>
