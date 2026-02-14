<script lang="ts">
  interface Props {
    value: string;
  }

  let { value = $bindable() }: Props = $props();
</script>

<textarea
  bind:value
  spellcheck="false"
  placeholder={"---\nname: Your Name\ntitle: Software Engineer\nemail: you@example.com\n---\n\n## Experience\n\n**Company** | Role | 2020 - Present\n\n- Did amazing things"}
></textarea>

<style>
  textarea {
    width: 100%;
    height: 100%;
    resize: none;
    border: none;
    padding: 1rem;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 0.875rem;
    line-height: 1.6;
    background: #1e1e2e;
    color: #cdd6f4;
    outline: none;
    tab-size: 2;
  }

  textarea::placeholder {
    color: #585b70;
  }
</style>
