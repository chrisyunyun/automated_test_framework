<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  isDark: {
    type: Boolean,
    default: true
  }
})

const cases = ref([])
const selectedCases = ref([])
const filterModule = ref('all')
const filterMarker = ref('all')
const isRunning = ref(false)
const logs = ref([])
const stats = ref({ passed: 0, failed: 0, skipped: 0, duration: 0 })
const history = ref([])
const selectedHistory = ref(null)
const generateReport = ref(false)

const modules = computed(() => {
  const mods = [...new Set(cases.value.map(c => c.module))]
  return ['all', ...mods]
})

const markers = computed(() => {
  const marks = [...new Set(cases.value.map(c => c.marker))]
  return ['all', ...marks]
})

const filteredCases = computed(() => {
  return cases.value.filter(c => {
    const moduleMatch = filterModule.value === 'all' || c.module === filterModule.value
    const markerMatch = filterMarker.value === 'all' || c.marker === filterMarker.value
    return moduleMatch && markerMatch
  })
})

const theme = computed(() => ({
  card: props.isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200',
  cardAlt: props.isDark ? 'bg-gray-700/50' : 'bg-gray-100',
  border: props.isDark ? 'border-gray-700' : 'border-gray-200',
  text: props.isDark ? 'text-gray-100' : 'text-gray-900',
  textMuted: props.isDark ? 'text-gray-400' : 'text-gray-600',
  textMuted2: props.isDark ? 'text-gray-500' : 'text-gray-400',
  btn: props.isDark ? 'bg-gray-700 hover:bg-gray-600 text-gray-100' : 'bg-gray-200 hover:bg-gray-300 text-gray-800',
  input: props.isDark ? 'bg-gray-700 border-gray-600 text-gray-100' : 'bg-gray-100 border-gray-300 text-gray-900',
  inputAlt: props.isDark ? 'bg-gray-900' : 'bg-gray-50',
  logText: props.isDark ? 'text-gray-300' : 'text-gray-700',
  logBorder: props.isDark ? 'border-gray-600' : 'border-gray-300',
  header: props.isDark ? 'border-gray-700' : 'border-gray-200',
  selected: props.isDark ? 'bg-blue-600/20 border-blue-500' : 'bg-blue-100 border-blue-500',
  unselected: props.isDark ? 'bg-gray-700/50 border-gray-600 hover:border-gray-500' : 'bg-gray-100 border-gray-300 hover:border-gray-400',
  statCard: props.isDark ? 'bg-gray-700/50' : 'bg-gray-100',
  badge: props.isDark ? 'text-gray-300' : 'text-gray-700',
  historyItem: props.isDark ? 'bg-gray-700/30 hover:bg-gray-700/50' : 'bg-gray-100 hover:bg-gray-200',
  historyActive: props.isDark ? 'bg-blue-600/20 border-blue-500' : 'bg-blue-100 border-blue-500',
}))

const fetchCases = async () => {
  try {
    const res = await axios.get('/api/cases')
    cases.value = res.data
  } catch (err) {
    logs.value.push({ type: 'error', content: `获取用例失败: ${err.message}` })
  }
}

const fetchHistory = async () => {
  try {
    const res = await axios.get('/api/history')
    history.value = res.data
  } catch (err) {
    console.error('获取历史记录失败:', err)
  }
}

const toggleCase = (caseId) => {
  const idx = selectedCases.value.indexOf(caseId)
  if (idx === -1) {
    selectedCases.value.push(caseId)
  } else {
    selectedCases.value.splice(idx, 1)
  }
}

const selectAll = () => {
  selectedCases.value = filteredCases.value.map(c => c.id)
}

const deselectAll = () => {
  selectedCases.value = []
}

const showHistoryDetail = (item) => {
  selectedHistory.value = item
  logs.value = []
  logs.value.push({ type: 'info', content: '========== 历史记录 #' + item.execution_id.slice(0, 8) + ' ==========' })
  logs.value.push({ type: 'info', content: '执行时间: ' + new Date(item.timestamp).toLocaleString() })
  logs.value.push({ type: 'info', content: `用例数量: ${item.case_ids.split(',').length}` })
  logs.value.push({ type: 'info', content: '========== 执行结果 ==========' })
  logs.value.push({ type: 'info', content: `通过: ${item.passed}` })
  logs.value.push({ type: 'info', content: `失败: ${item.failed}` })
  logs.value.push({ type: 'info', content: `跳过: ${item.skipped}` })
  logs.value.push({ type: 'info', content: `耗时: ${item.duration.toFixed(2)}s` })
  logs.value.push({ type: 'info', content: `状态: ${item.status}` })

  if (item.log) {
    logs.value.push({ type: 'info', content: '' })
    logs.value.push({ type: 'info', content: '--- 日志输出 ---' })
    const logContent = item.log.split('\n').slice(-30)
    for (const line of logContent) {
      if (line.trim()) {
        const type = line.includes('PASSED') ? 'pass' :
                     line.includes('FAILED') ? 'fail' :
                     line.includes('SKIPPED') ? 'skip' : 'info'
        logs.value.push({ type, content: line })
      }
    }
  }

  stats.value = {
    passed: item.passed,
    failed: item.failed,
    skipped: item.skipped,
    duration: item.duration
  }
}

const runTests = async () => {
  if (selectedCases.value.length === 0) {
    logs.value.push({ type: 'warn', content: '请至少选择一个测试用例' })
    return
  }

  isRunning.value = true
  logs.value = []
  stats.value = { passed: 0, failed: 0, skipped: 0, duration: 0 }
  selectedHistory.value = null

  const logLines = []
  logLines.push({ type: 'info', content: `开始执行 ${selectedCases.value.length} 个用例...` })
  logLines.push({ type: 'info', content: '执行中，请稍候...' })
  logs.value = logLines

  try {
    const res = await axios.post('/api/execute', null, {
      params: { case_ids: selectedCases.value.join(',') }
    })

    logs.value = []
    logs.value.push({ type: 'info', content: '========== 执行结果 ==========' })
    logs.value.push({ type: 'info', content: `通过: ${res.data.passed}` })
    logs.value.push({ type: 'info', content: `失败: ${res.data.failed}` })
    logs.value.push({ type: 'info', content: `跳过: ${res.data.skipped}` })
    logs.value.push({ type: 'info', content: `耗时: ${res.data.duration.toFixed(2)}s` })
    logs.value.push({ type: 'info', content: `状态: ${res.data.status}` })
    logs.value.push({ type: 'info', content: '================================' })

    if (res.data.log) {
      logs.value.push({ type: 'info', content: '' })
      logs.value.push({ type: 'info', content: '--- 日志输出 ---' })
      const logContent = res.data.log.split('\n').slice(-30)
      for (const line of logContent) {
        if (line.trim()) {
          const type = line.includes('PASSED') ? 'pass' :
                       line.includes('FAILED') ? 'fail' :
                       line.includes('SKIPPED') ? 'skip' : 'info'
          logs.value.push({ type, content: line })
        }
      }
    }

    stats.value = {
      passed: res.data.passed,
      failed: res.data.failed,
      skipped: res.data.skipped,
      duration: res.data.duration
    }

    fetchHistory()
  } catch (err) {
    logs.value.push({ type: 'error', content: `执行失败: ${err.message}` })
  } finally {
    isRunning.value = false
  }
}

const stopTests = async () => {
  logs.value.push({ type: 'warn', content: '停止执行...' })
  isRunning.value = false
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

onMounted(() => {
  fetchCases()
  fetchHistory()
})
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2 space-y-6">
      <div :class="theme.card + ' rounded-xl p-6 border'">
        <div class="flex items-center justify-between mb-4">
          <h2 :class="'text-xl font-semibold ' + theme.text">测试用例</h2>
          <div class="flex gap-2">
            <button @click="selectAll" :class="theme.btn + ' px-3 py-1 text-sm rounded-lg transition'">全选</button>
            <button @click="deselectAll" :class="theme.btn + ' px-3 py-1 text-sm rounded-lg transition'">取消全选</button>
          </div>
        </div>

        <div class="flex gap-4 mb-4">
          <select v-model="filterModule" :class="theme.input + ' border rounded-lg px-3 py-2 text-sm'">
            <option v-for="mod in modules" :key="mod" :value="mod">
              {{ mod === 'all' ? '全部模块' : mod }}
            </option>
          </select>
          <select v-model="filterMarker" :class="theme.input + ' border rounded-lg px-3 py-2 text-sm'">
            <option v-for="mark in markers" :key="mark" :value="mark">
              {{ mark === 'all' ? '全部类型' : (mark === 'smoke' ? '冒烟测试' : '回归测试') }}
            </option>
          </select>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto pr-2">
          <div
            v-for="testCase in filteredCases"
            :key="testCase.id"
            @click="toggleCase(testCase.id)"
            :class="[
              'p-4 rounded-lg border cursor-pointer transition-all',
              selectedCases.includes(testCase.id) ? theme.selected : theme.unselected
            ]"
          >
            <div class="flex items-start gap-3">
              <div :class="[
                'w-5 h-5 mt-0.5 rounded border flex items-center justify-center flex-shrink-0',
                selectedCases.includes(testCase.id) ? 'bg-blue-500 border-blue-500' : theme.logBorder
              ]">
                <svg v-if="selectedCases.includes(testCase.id)" class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p :class="'font-medium text-sm truncate ' + theme.text">{{ testCase.name }}</p>
                <p :class="'text-xs ' + theme.textMuted + ' mt-1'">{{ testCase.module }}</p>
                <span :class="[
                  'inline-block mt-2 px-2 py-0.5 text-xs rounded-full',
                  testCase.marker === 'smoke' ? 'bg-green-600/30 text-green-400' : 'bg-yellow-600/30 text-yellow-400'
                ]">
                  {{ testCase.marker === 'smoke' ? '冒烟' : '回归' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div :class="'mt-4 pt-4 ' + theme.header + ' flex items-center justify-between border-t'">
          <div class="flex items-center gap-4">
            <span :class="'text-sm ' + theme.textMuted">
              已选择: <span :class="theme.text + ' font-medium'">{{ selectedCases.length }}</span> / {{ filteredCases.length }} 个用例
            </span>
          </div>
          <div class="flex gap-3">
            <button
              @click="stopTests"
              :disabled="!isRunning"
              :class="[
                'px-6 py-2 rounded-lg font-medium transition',
                isRunning ? 'bg-red-600 hover:bg-red-700' : 'bg-gray-400 cursor-not-allowed'
              ]"
            >
              停止
            </button>
            <button
              @click="runTests"
              :disabled="isRunning || selectedCases.length === 0"
              :class="[
                'px-6 py-2 rounded-lg font-medium transition flex items-center gap-1',
                (isRunning || selectedCases.length === 0) ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
              ]"
            >
              <span v-if="isRunning" class="animate-pulse">执行中</span>
              <span v-else>运行测试</span>
            </button>
          </div>
        </div>
      </div>

      <div :class="theme.card + ' rounded-xl p-6 border'">
        <div class="flex items-center justify-between mb-4">
          <h2 :class="'text-xl font-semibold ' + theme.text">
            {{ selectedHistory ? '历史记录详情' : '执行日志' }}
          </h2>
          <button @click="logs = []" :class="'text-sm ' + theme.textMuted + ' hover:' + theme.text + ' transition'">清空</button>
        </div>
        <div :class="theme.inputAlt + ' rounded-lg p-4 h-80 overflow-y-auto font-mono text-sm space-y-1 border'">
          <div v-for="(log, idx) in logs" :key="idx" :class="[
            'flex gap-3',
            log.type === 'pass' ? 'text-green-400' :
            log.type === 'fail' ? 'text-red-400' :
            log.type === 'skip' ? 'text-yellow-400' :
            log.type === 'error' ? 'text-red-500' :
            log.type === 'warn' ? 'text-yellow-500' : theme.logText
          ]">
            <span class="flex-1 break-all">{{ log.content }}</span>
          </div>
          <div v-if="logs.length === 0" :class="theme.textMuted + ' text-center py-8'">
            暂无日志。点击"运行测试"开始执行。
          </div>
        </div>
      </div>
    </div>

    <div class="space-y-6">
      <div :class="theme.card + ' rounded-xl p-6 border'">
        <h2 :class="'text-xl font-semibold mb-4 ' + theme.text">执行结果</h2>
        <div class="grid grid-cols-2 gap-4">
          <div :class="theme.statCard + ' rounded-lg p-4 text-center'">
            <p class="text-3xl font-bold text-green-400">{{ stats.passed }}</p>
            <p :class="'text-sm ' + theme.textMuted + ' mt-1'">通过</p>
          </div>
          <div :class="theme.statCard + ' rounded-lg p-4 text-center'">
            <p class="text-3xl font-bold text-red-400">{{ stats.failed }}</p>
            <p :class="'text-sm ' + theme.textMuted + ' mt-1'">失败</p>
          </div>
          <div :class="theme.statCard + ' rounded-lg p-4 text-center'">
            <p class="text-3xl font-bold text-yellow-400">{{ stats.skipped }}</p>
            <p :class="'text-sm ' + theme.textMuted + ' mt-1'">跳过</p>
          </div>
          <div :class="theme.statCard + ' rounded-lg p-4 text-center'">
            <p class="text-3xl font-bold text-blue-400">{{ stats.duration.toFixed(2) }}s</p>
            <p :class="'text-sm ' + theme.textMuted + ' mt-1'">耗时</p>
          </div>
        </div>
      </div>

      <div :class="theme.card + ' rounded-xl p-6 border'">
        <h2 :class="'text-xl font-semibold mb-4 ' + theme.text">执行历史</h2>
        <div class="space-y-2 max-h-80 overflow-y-auto">
          <div v-if="history.length === 0" :class="'text-sm ' + theme.textMuted + ' text-center py-4'">
            暂无历史记录
          </div>
          <div
            v-for="item in history"
            :key="item.execution_id"
            @click="showHistoryDetail(item)"
            :class="[
              'p-3 rounded-lg border cursor-pointer transition-all',
              selectedHistory?.execution_id === item.execution_id ? theme.historyActive : theme.historyItem
            ]"
          >
            <div class="flex items-center justify-between mb-1">
              <span :class="'text-xs ' + theme.textMuted">{{ formatTime(item.timestamp) }}</span>
              <span :class="[
                'text-xs px-2 py-0.5 rounded-full',
                item.status === 'passed' ? 'bg-green-600/30 text-green-400' :
                item.status === 'failed' ? 'bg-red-600/30 text-red-400' :
                'bg-gray-600/30 text-gray-400'
              ]">
                {{ item.status }}
              </span>
            </div>
            <div :class="'text-sm ' + theme.text">
              <span class="text-green-400">{{ item.passed }}</span>
              <span :class="'mx-1 ' + theme.textMuted">/</span>
              <span class="text-red-400">{{ item.failed }}</span>
              <span :class="'mx-1 ' + theme.textMuted">/</span>
              <span class="text-yellow-400">{{ item.skipped }}</span>
            </div>
          </div>
        </div>
      </div>

      <div :class="theme.card + ' rounded-xl p-6 border'">
        <h2 :class="'text-xl font-semibold mb-4 ' + theme.text">快速统计</h2>
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span :class="theme.textMuted">用例总数</span>
            <span :class="theme.text + ' font-medium'">{{ cases.length }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span :class="theme.textMuted">冒烟测试</span>
            <span class="font-medium text-green-400">{{ cases.filter(c => c.marker === 'smoke').length }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span :class="theme.textMuted">回归测试</span>
            <span class="font-medium text-yellow-400">{{ cases.filter(c => c.marker === 'regression').length }}</span>
          </div>
        </div>
      </div>

      <div :class="theme.card + ' rounded-xl p-6 border'">
        <h2 :class="'text-xl font-semibold mb-4 ' + theme.text">图例</h2>
        <div class="space-y-2 text-sm">
          <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-green-400"></span>
            <span :class="theme.badge">冒烟测试</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-yellow-400"></span>
            <span :class="theme.badge">回归测试</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-blue-500"></span>
            <span :class="theme.badge">已选中</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
