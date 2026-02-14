<script lang="ts">
  interface Props {
    templates: string[];
    selected: string;
  }

  let { templates, selected = $bindable() }: Props = $props();
</script>

<select bind:value={selected}>
  {#each templates as t}
    <option value={t}>{t}</option>
  {/each}
</select>

<style>
  select {
    padding: 0.4rem 0.8rem;
    border: 1px solid #45475a;
    border-radius: 6px;
    background: #313244;
    color: #cdd6f4;
    font-size: 0.875rem;
    cursor: pointer;
    outline: none;
  }

  select:hover {
    border-color: #89b4fa;
  }
</style>
