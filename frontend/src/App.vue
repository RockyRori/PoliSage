<!-- src/App.vue -->
<template>
  <n-config-provider>
    <div class="container mx-auto p-4 space-y-8">
      <!-- 文档列表区域 -->
      <DocumentList />
    </div>
  </n-config-provider>
</template>

<script setup>
import DocumentList from '@/components/DocumentList.vue'
</script>

<style>
.container {
  max-width: 800px;
}
</style>
