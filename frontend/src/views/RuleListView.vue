<script setup>
import { onMounted, ref } from 'vue'

import EmptyState from '../components/common/EmptyState.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import RuleCard from '../components/rule/RuleCard.vue'
import { listRules } from '../api/rules'


const loading = ref(false)
const rules = ref([])

onMounted(async () => {
  loading.value = true
  try {
    const response = await listRules()
    rules.value = response.data?.results || response.data || []
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="page-panel">
    <h1>规则条目</h1>
    <loading-spinner v-if="loading" />
    <empty-state v-else-if="rules.length === 0">暂无规则数据，等待导入。</empty-state>
    <div v-else class="card-grid">
      <rule-card v-for="rule in rules" :key="rule.slug" :rule="rule" />
    </div>
  </section>
</template>
