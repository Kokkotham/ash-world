<script setup>
import { onMounted, ref } from 'vue'

import EmptyState from '../components/common/EmptyState.vue'
import GlossaryList from '../components/glossary/GlossaryList.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import { listGlossaryTerms } from '../api/glossary'


const loading = ref(false)
const terms = ref([])

onMounted(async () => {
  loading.value = true
  try {
    const response = await listGlossaryTerms()
    terms.value = response.data?.results || response.data || []
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="page-panel">
    <h1>术语词条</h1>
    <loading-spinner v-if="loading" />
    <empty-state v-else-if="terms.length === 0">暂无术语数据，等待导入。</empty-state>
    <glossary-list v-else :terms="terms" />
  </section>
</template>
