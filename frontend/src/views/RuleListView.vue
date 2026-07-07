<script setup>
import { computed, onMounted, ref } from 'vue'

import EmptyState from '../components/common/EmptyState.vue'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import RuleCard from '../components/rule/RuleCard.vue'
import { getRule, listRuleCategories, listRules } from '../api/rules'


const loading = ref(false)
const detailLoading = ref(false)
const error = ref('')
const detailError = ref('')
const categories = ref([])
const rules = ref([])
const selectedCategory = ref('all')
const selectedRule = ref(null)

const visibleRules = computed(() => {
  if (selectedCategory.value === 'all') return rules.value
  return rules.value.filter((rule) => rule.category?.slug === selectedCategory.value)
})

const activeCategoryName = computed(() => {
  if (selectedCategory.value === 'all') return '全部规则'
  return categories.value.find((category) => category.slug === selectedCategory.value)?.name || '当前分类'
})

function unwrapList(data) {
  return data?.results || data || []
}

function summarizeContent(rule) {
  if (!rule) return []
  if (Array.isArray(rule.content_blocks) && rule.content_blocks.length > 0) {
    return rule.content_blocks
  }
  if (rule.content) {
    return String(rule.content).split(/\n+/).filter(Boolean).slice(0, 8)
  }
  if (rule.summary) return [rule.summary]
  return []
}

async function loadInitialData() {
  loading.value = true
  error.value = ''
  try {
    const [categoryResponse, ruleResponse] = await Promise.all([
      listRuleCategories(),
      listRules()
    ])
    categories.value = unwrapList(categoryResponse.data)
    rules.value = unwrapList(ruleResponse.data)
    selectedRule.value = rules.value[0] || null
  } catch (err) {
    error.value = err?.response?.data?.detail || err?.message || '规则数据读取失败，请确认后端服务已启动。'
  } finally {
    loading.value = false
  }
}

function selectCategory(slug) {
  selectedCategory.value = slug
  detailError.value = ''
  selectedRule.value = visibleRules.value[0] || null
}

async function selectRule(rule) {
  if (!rule) return
  selectedRule.value = rule
  detailError.value = ''
  detailLoading.value = true
  try {
    const response = await getRule(rule.slug)
    selectedRule.value = response.data
  } catch (err) {
    detailError.value = err?.response?.data?.detail || err?.message || '规则详情读取失败。'
  } finally {
    detailLoading.value = false
  }
}

onMounted(loadInitialData)
</script>

<template>
  <section class="rulebook-page">
    <div class="rulebook-heading">
      <p class="eyebrow">Beta 规则书</p>
      <h1>灰烬世界规则书</h1>
      <p>当前展示已导入的核心属性与种族规则。</p>
    </div>

    <loading-spinner v-if="loading" />
    <div v-else-if="error" class="error-state">{{ error }}</div>
    <empty-state v-else-if="rules.length === 0">暂无规则数据，等待导入。</empty-state>

    <div v-else class="rulebook-layout">
      <aside class="category-panel" aria-label="规则分类">
        <h2>分类</h2>
        <button
          class="category-button"
          :class="{ active: selectedCategory === 'all' }"
          type="button"
          @click="selectCategory('all')"
        >
          <span>全部规则</span>
          <strong>{{ rules.length }}</strong>
        </button>
        <button
          v-for="category in categories"
          :key="category.slug"
          class="category-button"
          :class="{ active: selectedCategory === category.slug }"
          type="button"
          @click="selectCategory(category.slug)"
        >
          <span>{{ category.name }}</span>
          <strong>{{ rules.filter((rule) => rule.category?.slug === category.slug).length }}</strong>
        </button>
      </aside>

      <section class="rule-list-panel" aria-label="规则列表">
        <div class="panel-heading">
          <h2>{{ activeCategoryName }}</h2>
          <span>{{ visibleRules.length }} 条</span>
        </div>
        <empty-state v-if="visibleRules.length === 0">当前分类暂无规则。</empty-state>
        <button
          v-for="rule in visibleRules"
          v-else
          :key="rule.slug"
          class="rule-card-button"
          type="button"
          @click="selectRule(rule)"
        >
          <rule-card :rule="rule" :active="selectedRule?.slug === rule.slug" />
        </button>
      </section>

      <article class="rule-detail-panel" aria-label="规则详情">
        <loading-spinner v-if="detailLoading" />
        <div v-else-if="selectedRule">
          <p class="eyebrow">{{ selectedRule.category?.name || '未分类' }}</p>
          <h2>{{ selectedRule.title }}</h2>
          <div class="rule-meta">
            <span>{{ selectedRule.rule_type || '规则' }}</span>
            <span>{{ selectedRule.chapter_ref || '未分章' }}</span>
            <span>{{ selectedRule.version_status || 'draft' }}</span>
          </div>
          <p v-if="selectedRule.summary" class="rule-summary">{{ selectedRule.summary }}</p>
          <div v-if="detailError" class="error-state compact">{{ detailError }}</div>
          <div class="rule-content">
            <template v-for="(block, index) in summarizeContent(selectedRule)" :key="index">
              <p v-if="typeof block === 'string'">{{ block }}</p>
              <pre v-else>{{ JSON.stringify(block, null, 2) }}</pre>
            </template>
          </div>
        </div>
        <empty-state v-else>请选择一条规则查看详情。</empty-state>
      </article>
    </div>
  </section>
</template>
