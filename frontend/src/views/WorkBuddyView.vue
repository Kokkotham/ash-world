<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const STORAGE_KEY = 'embers-world-workbuddy-handoffs'

const defaultSummary = 'Embers World 当前处于 Vue3 + Django 最小可运行骨架阶段。已新增 backend/frontend、docker-compose MySQL 8.0、.env.example。尚未开发角色卡、用户系统、战役系统，也尚未改旧静态页面。后续应按模块逐步开发，每个模块完成后输出完成报告。'

const form = reactive({
  summary: defaultSummary,
  title: '',
  type: '开发',
  priority: '中',
  description: '',
  assignee: 'Codex'
})

const records = ref([])
const generatedText = ref('')
const copyMessage = ref('')

const taskTypes = ['开发', '修复', '文档', '部署', '规则整理']
const priorities = ['高', '中', '低']
const assignees = ['Codex', 'ChatGPT', 'WorkBuddy', '人工确认']

const canGenerate = computed(() => form.title.trim() && form.description.trim())

function loadRecords() {
  try {
    records.value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    records.value = []
  }
}

function saveRecords() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records.value))
}

function buildHandoffText() {
  return `【Embers World / WorkBuddy 对接任务】

任务标题：
${form.title.trim()}

任务类型：
${form.type}

优先级：
${form.priority}

任务说明：
${form.description.trim()}

下一步执行者：
${form.assignee}

执行要求：

* 每次只做一个模块
* 修改完成后输出完成报告
* 报告必须包含：修改文件、接口变化、数据库变化、测试结果、遗留 TODO
* 不要擅自扩大范围
* 视觉风格保持黑金暗黑幻想`
}

function generateHandoff() {
  if (!canGenerate.value) return
  generatedText.value = buildHandoffText()
  const record = {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    createdAt: new Date().toLocaleString('zh-CN', { hour12: false }),
    title: form.title.trim(),
    type: form.type,
    priority: form.priority,
    assignee: form.assignee,
    text: generatedText.value
  }
  records.value = [record, ...records.value]
  saveRecords()
  copyMessage.value = '交接文本已生成并保存'
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
    copyMessage.value = '复制成功'
  } catch {
    copyMessage.value = '复制失败，请手动选择文本复制'
  }
}

function deleteRecord(id) {
  records.value = records.value.filter((record) => record.id !== id)
  saveRecords()
}

function clearForm() {
  form.title = ''
  form.type = '开发'
  form.priority = '中'
  form.description = ''
  form.assignee = 'Codex'
  generatedText.value = ''
  copyMessage.value = ''
}

onMounted(loadRecords)
</script>

<template>
  <div class="workbuddy-page">
    <section class="workbuddy-hero">
      <p class="eyebrow">本地交接模式</p>
      <h1>WorkBuddy 对接窗口</h1>
      <p>
        用于整理 Embers World 的开发交接、任务分发与上下文同步。当前为本地交接模式，不会自动连接外部系统。
      </p>
    </section>

    <section class="workbuddy-grid">
      <article class="workbuddy-card status-card">
        <h2>对接状态</h2>
        <dl>
          <div>
            <dt>WorkBuddy 对接状态</dt>
            <dd>未连接</dd>
          </div>
          <div>
            <dt>当前项目</dt>
            <dd>Embers World</dd>
          </div>
          <div>
            <dt>当前阶段</dt>
            <dd>任务001后，准备进入功能模块开发</dd>
          </div>
          <div>
            <dt>当前模式</dt>
            <dd>本地交接窗口</dd>
          </div>
        </dl>
        <p class="notice">当前页面仅用于交接记录，不会自动同步外部系统。</p>
      </article>

      <article class="workbuddy-card summary-card">
        <h2>交接摘要</h2>
        <label for="handoff-summary">当前项目摘要</label>
        <textarea id="handoff-summary" v-model="form.summary" rows="7" />
      </article>
    </section>

    <section class="workbuddy-card">
      <h2>任务对接</h2>
      <div class="task-form">
        <label>
          <span>任务标题</span>
          <input v-model="form.title" type="text" placeholder="例如：实现最小规则数据导入" />
        </label>

        <label>
          <span>任务类型</span>
          <select v-model="form.type">
            <option v-for="type in taskTypes" :key="type" :value="type">{{ type }}</option>
          </select>
        </label>

        <label>
          <span>优先级</span>
          <select v-model="form.priority">
            <option v-for="priority in priorities" :key="priority" :value="priority">{{ priority }}</option>
          </select>
        </label>

        <label>
          <span>下一步交给谁</span>
          <select v-model="form.assignee">
            <option v-for="assignee in assignees" :key="assignee" :value="assignee">{{ assignee }}</option>
          </select>
        </label>

        <label class="wide-field">
          <span>任务说明</span>
          <textarea v-model="form.description" rows="6" placeholder="写清楚任务范围、禁止事项、验收标准。" />
        </label>
      </div>

      <div class="button-row">
        <button class="gold-button" type="button" :disabled="!canGenerate" @click="generateHandoff">
          生成交接文本
        </button>
        <button class="dark-button" type="button" @click="clearForm">清空表单</button>
        <span class="copy-message" aria-live="polite">{{ copyMessage }}</span>
      </div>

      <div v-if="generatedText" class="generated-panel">
        <div class="generated-header">
          <h3>生成结果</h3>
          <button class="dark-button" type="button" @click="copyText(generatedText)">复制文本</button>
        </div>
        <pre>{{ generatedText }}</pre>
      </div>
    </section>

    <section class="workbuddy-card">
      <h2>交接记录</h2>
      <p v-if="records.length === 0" class="empty-copy">暂无交接记录。</p>
      <div v-else class="record-list">
        <article v-for="record in records" :key="record.id" class="record-card">
          <div class="record-meta">
            <div>
              <h3>{{ record.title }}</h3>
              <p>{{ record.createdAt }} · 优先级：{{ record.priority }} · 下一步执行者：{{ record.assignee }}</p>
            </div>
            <div class="record-actions">
              <button class="dark-button" type="button" @click="copyText(record.text)">复制文本</button>
              <button class="danger-button" type="button" @click="deleteRecord(record.id)">删除记录</button>
            </div>
          </div>
          <pre>{{ record.text }}</pre>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.workbuddy-page {
  display: grid;
  gap: 24px;
}

.workbuddy-hero,
.workbuddy-card {
  border: 1px solid var(--border-gold);
  background: linear-gradient(145deg, rgba(20, 20, 20, 0.96), rgba(10, 10, 10, 0.92));
  padding: 28px;
}

.workbuddy-hero h1,
.workbuddy-card h2,
.generated-panel h3,
.record-card h3 {
  color: var(--gold);
  font-family: var(--font-heading);
}

.workbuddy-hero h1,
.workbuddy-card h2 {
  margin: 0 0 14px;
}

.workbuddy-hero p,
.notice,
.empty-copy,
.record-meta p {
  color: var(--text-secondary);
  line-height: 1.7;
}

.workbuddy-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  gap: 24px;
}

.status-card dl {
  display: grid;
  gap: 12px;
  margin: 0;
}

.status-card dl div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid rgba(201, 168, 76, 0.12);
  padding-bottom: 10px;
}

.status-card dt {
  color: var(--text-secondary);
}

.status-card dd {
  margin: 0;
  color: var(--text-primary);
  text-align: right;
}

label {
  display: grid;
  gap: 8px;
  color: var(--text-secondary);
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid rgba(201, 168, 76, 0.24);
  background: rgba(5, 5, 5, 0.72);
  color: var(--text-primary);
  font: inherit;
  padding: 11px 12px;
  outline: none;
}

textarea {
  resize: vertical;
  line-height: 1.65;
}

input:focus,
select:focus,
textarea:focus {
  border-color: var(--gold);
  box-shadow: 0 0 0 2px rgba(201, 168, 76, 0.12);
}

.task-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.wide-field {
  grid-column: 1 / -1;
}

.button-row,
.generated-header,
.record-meta,
.record-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.button-row {
  flex-wrap: wrap;
  margin-top: 20px;
}

button {
  cursor: pointer;
  font: inherit;
  transition: border-color 0.2s ease, background 0.2s ease, color 0.2s ease;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.gold-button,
.dark-button,
.danger-button {
  border: 1px solid var(--border-gold);
  background: rgba(26, 26, 26, 0.92);
  color: var(--text-primary);
  padding: 10px 16px;
}

.gold-button {
  border-color: var(--gold);
  color: var(--gold);
}

.gold-button:not(:disabled):hover,
.dark-button:hover {
  background: rgba(201, 168, 76, 0.12);
  border-color: var(--gold);
}

.danger-button {
  border-color: rgba(139, 32, 32, 0.75);
  color: #d48a8a;
}

.danger-button:hover {
  background: rgba(139, 32, 32, 0.16);
}

.copy-message {
  color: var(--text-secondary);
}

.generated-panel,
.record-card {
  margin-top: 20px;
  border: 1px solid rgba(201, 168, 76, 0.16);
  background: rgba(5, 5, 5, 0.45);
  padding: 18px;
}

.generated-header,
.record-meta {
  justify-content: space-between;
  align-items: flex-start;
}

pre {
  margin: 14px 0 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--text-primary);
  font-family: var(--font-body);
  line-height: 1.7;
}

.record-list {
  display: grid;
  gap: 18px;
}

.record-card h3 {
  margin: 0 0 6px;
}

@media (max-width: 820px) {
  .workbuddy-grid,
  .task-form {
    grid-template-columns: 1fr;
  }

  .record-meta,
  .record-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
