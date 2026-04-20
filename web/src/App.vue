<template>
  <div class="min-h-screen bg-gray-900 text-gray-100 p-6">
    <header class="mb-8">
      <h1 class="text-3xl font-bold text-white">Pytest Runner</h1>
      <p class="text-gray-400 mt-1">易威行 OA 自动化测试执行平台</p>
    </header>

    <TestRunner />
  </div>
</template>

<script setup>
import TestRunner from './views/TestRunner.vue'
</script>
