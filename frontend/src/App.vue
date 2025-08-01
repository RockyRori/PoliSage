<template>
  <n-config-provider>
    <div class="container mx-auto p-4">
      <!-- 顶部导航 Tab -->
      <n-tabs v-model:value="activeTab">
        <n-tab-pane name="chat" tab="智能问答" />
        <n-tab-pane name="docs" tab="文档列表" />
      </n-tabs>

      <!-- 内容区域 -->
      <div class="mt-6">
        <ChatPage v-if="activeTab === 'chat'" />
        <DocumentList v-else />

      </div>
    </div>
  </n-config-provider>
</template>

<script setup>
import { ref } from 'vue'
import DocumentList from '@/components/DocumentList.vue'
import ChatPage from '@/components/ChatPage.vue'

// 当前激活 Tab，默认为文档列表
const activeTab = ref('docs')
</script>

<style>
.container {
  max-width: 800px;
}
</style>
