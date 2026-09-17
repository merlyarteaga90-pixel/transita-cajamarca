<script lang="ts">
  import { hasValue } from '../lib/formatters';

  export let metrics: Array<[string, string, string]> = [];

  $: visibleMetrics = metrics.filter(([, , value]) => hasValue(value));
</script>

{#if visibleMetrics.length}
  <div class="metricas-grid">
    {#each visibleMetrics as [icon, label, value]}
      <div class="metrica-card">
        <span class="metrica-icono">{icon}</span>
        <span class="metrica-label">{label}</span>
        <strong class="metrica-valor">{value}</strong>
      </div>
    {/each}
  </div>
{/if}
