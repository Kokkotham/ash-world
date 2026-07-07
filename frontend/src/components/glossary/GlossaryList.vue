<script setup>
defineProps({
  terms: {
    type: Array,
    default: () => []
  }
})
</script>

<template>
  <div class="glossary-list">
    <article v-for="term in terms" :key="term.key" class="rule-card">
      <h3>{{ term.term }}</h3>
      <p>{{ term.definition }}</p>
      <small>{{ term.category || '未分类' }}</small>
    </article>
  </div>
</template>
