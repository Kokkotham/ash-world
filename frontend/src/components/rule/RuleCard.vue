<script setup>
defineProps({
  rule: {
    type: Object,
    required: true
  },
  active: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <article class="rule-card" :class="{ active }">
    <h3>{{ rule.title }}</h3>
    <p>{{ rule.summary || '暂无摘要' }}</p>
    <small>
      {{ rule.category?.name || '未分类' }} · {{ rule.chapter_ref || '未分章' }}
    </small>
  </article>
</template>
