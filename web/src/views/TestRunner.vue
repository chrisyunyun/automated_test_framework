<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const cases = ref([])
const selectedCases = ref([])
const filterModule = ref('all')
const filterMarker = ref('all')
const isRunning = ref(false)
const executionId = ref('')
const logs = ref([])
const stats = ref({ passed: 0, failed: 0, skipped: 0, duration: 0 })
const logContainer = ref(null)

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

const fetchCases = async () => {
  try {
    const res = await axios.get('/api/cases')
    cases.value = res.data
  } catch (err) {
    addLog('error', `Failed to fetch cases: ${err.message}`)
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

const addLog = (type, content) => {
  const timestamp = new Date().toLocaleTimeString()
  logs.value.push({ type, content, timestamp })
  if (logContainer.value) {
    setTimeout(() => {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }, 10)
  }
}

const runTests = async () => {
  if (selectedCases.value.length === 0) {
    addLog('warn', 'Please select at least one test case')
    return
  }

  isRunning.value = true
  executionId.value = ''
  logs.value = []
  stats.value = { passed: 0, failed: 0, skipped: 0, duration: 0 }

  try {
    const res = await axios.post('/api/execute', null, {
      params: { case_ids: selectedCases.value.join(',') }
    })
    executionId.value = res.data.execution_id
    addLog('info', `Starting execution (ID: ${executionId.value})...`)
    addLog('info', `Selected ${selectedCases.value.length} case(s)`)

    const eventSource = new EventSource(`/api/execute/${executionId.value}/stream?case_ids=${selectedCases.value.join(',')}`)

    eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        eventSource.close()
        isRunning.value = false
        addLog('info', 'Execution completed')
        return
      }

      try {
        const data = JSON.parse(event.data)

        if (data.type === 'log') {
          const type = data.content.includes('PASSED') ? 'pass' :
                       data.content.includes('FAILED') ? 'fail' :
                       data.content.includes('SKIPPED') ? 'skip' : 'info'
          addLog(type, data.content)
        } else if (data.type === 'result') {
          stats.value = {
            passed: data.passed,
            failed: data.failed,
            skipped: data.skipped,
            duration: data.duration.toFixed(2)
          }
        } else if (data.type === 'error') {
          addLog('error', data.message)
        }
      } catch (e) {
        addLog('info', event.data)
      }
    }

    eventSource.onerror = () => {
      eventSource.close()
      isRunning.value = false
      addLog('error', 'Connection lost')
    }
  } catch (err) {
    addLog('error', `Failed to start: ${err.message}`)
    isRunning.value = false
  }
}

const stopTests = async () => {
  if (executionId.value) {
    await axios.delete(`/api/execute/${executionId.value}`)
    addLog('warn', 'Execution stopped by user')
    isRunning.value = false
  }
}

onMounted(() => {
  fetchCases()
})
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <div class="lg:col-span-2 space-y-6">
      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold">Test Cases</h2>
          <div class="flex gap-2">
            <button @click="selectAll" class="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded-lg transition">Select All</button>
            <button @click="deselectAll" class="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded-lg transition">Deselect All</button>
          </div>
        </div>

        <div class="flex gap-4 mb-4">
          <select v-model="filterModule" class="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm">
            <option v-for="mod in modules" :key="mod" :value="mod">
              {{ mod === 'all' ? 'All Modules' : mod }}
            </option>
          </select>
          <select v-model="filterMarker" class="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm">
            <option v-for="mark in markers" :key="mark" :value="mark">
              {{ mark === 'all' ? 'All Markers' : mark }}
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
              selectedCases.includes(testCase.id)
                ? 'bg-blue-600/20 border-blue-500'
                : 'bg-gray-700/50 border-gray-600 hover:border-gray-500'
            ]"
          >
            <div class="flex items-start gap-3">
              <div :class="[
                'w-5 h-5 mt-0.5 rounded border flex items-center justify-center flex-shrink-0',
                selectedCases.includes(testCase.id) ? 'bg-blue-500 border-blue-500' : 'border-gray-500'
              ]">
                <svg v-if="selectedCases.includes(testCase.id)" class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-sm truncate">{{ testCase.name }}</p>
                <p class="text-xs text-gray-400 mt-1">{{ testCase.module }}</p>
                <span :class="[
                  'inline-block mt-2 px-2 py-0.5 text-xs rounded-full',
                  testCase.marker === 'smoke' ? 'bg-green-600/30 text-green-400' : 'bg-yellow-600/30 text-yellow-400'
                ]">
                  {{ testCase.marker }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-gray-700 flex items-center justify-between">
          <span class="text-sm text-gray-400">
            Selected: <span class="text-white font-medium">{{ selectedCases.length }}</span> / {{ filteredCases.length }} cases
          </span>
          <div class="flex gap-3">
            <button
              @click="stopTests"
              :disabled="!isRunning"
              class="px-6 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition"
            >
              Stop
            </button>
            <button
              @click="runTests"
              :disabled="isRunning || selectedCases.length === 0"
              class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition flex items-center gap-2"
            >
              <svg v-if="isRunning" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isRunning ? 'Running...' : 'Run Tests' }}
            </button>
          </div>
        </div>
      </div>

      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold">Console Output</h2>
          <button @click="logs = []" class="text-sm text-gray-400 hover:text-white transition">Clear</button>
        </div>
        <div
          ref="logContainer"
          class="bg-gray-900 rounded-lg p-4 h-80 overflow-y-auto font-mono text-sm space-y-1"
        >
          <div v-for="(log, idx) in logs" :key="idx" :class="[
            'flex gap-3',
            log.type === 'pass' ? 'text-green-400' :
            log.type === 'fail' ? 'text-red-400' :
            log.type === 'skip' ? 'text-yellow-400' :
            log.type === 'error' ? 'text-red-500' :
            log.type === 'warn' ? 'text-yellow-500' : 'text-gray-300'
          ]">
            <span class="text-gray-500 text-xs">{{ log.timestamp }}</span>
            <span class="flex-1 break-all">{{ log.content }}</span>
          </div>
          <div v-if="logs.length === 0" class="text-gray-500 text-center py-8">
            No output yet. Run tests to see logs.
          </div>
        </div>
      </div>
    </div>

    <div class="space-y-6">
      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 class="text-xl font-semibold mb-4">Execution Summary</h2>
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-gray-700/50 rounded-lg p-4 text-center">
            <p class="text-3xl font-bold text-green-400">{{ stats.passed }}</p>
            <p class="text-sm text-gray-400 mt-1">Passed</p>
          </div>
          <div class="bg-gray-700/50 rounded-lg p-4 text-center">
            <p class="text-3xl font-bold text-red-400">{{ stats.failed }}</p>
            <p class="text-sm text-gray-400 mt-1">Failed</p>
          </div>
          <div class="bg-gray-700/50 rounded-lg p-4 text-center">
            <p class="text-3xl font-bold text-yellow-400">{{ stats.skipped }}</p>
            <p class="text-sm text-gray-400 mt-1">Skipped</p>
          </div>
          <div class="bg-gray-700/50 rounded-lg p-4 text-center">
            <p class="text-3xl font-bold text-blue-400">{{ stats.duration }}s</p>
            <p class="text-sm text-gray-400 mt-1">Duration</p>
          </div>
        </div>
      </div>

      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 class="text-xl font-semibold mb-4">Quick Stats</h2>
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-gray-400">Total Cases</span>
            <span class="font-medium">{{ cases.length }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-gray-400">Smoke Tests</span>
            <span class="font-medium text-green-400">{{ cases.filter(c => c.marker === 'smoke').length }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-gray-400">Regression</span>
            <span class="font-medium text-yellow-400">{{ cases.filter(c => c.marker === 'regression').length }}</span>
          </div>
        </div>
      </div>

      <div class="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 class="text-xl font-semibold mb-4">Legend</h2>
        <div class="space-y-2 text-sm">
          <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-green-400"></span>
            <span class="text-gray-300">Smoke Test</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-yellow-400"></span>
            <span class="text-gray-300">Regression Test</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="w-3 h-3 rounded-full bg-blue-500"></span>
            <span class="text-gray-300">Selected</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
