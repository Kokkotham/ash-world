<script setup>
defineProps({
  rule: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <article class="rule-card">
    <h3>{{ rule.title }}</h3>
    <p>{{ rule.summary || '暂无摘要' }}</p>
    <small>{{ rule.rule_type }} · {{ rule.chapter_ref || '未分章' }}</small>
  </article>
</template>
