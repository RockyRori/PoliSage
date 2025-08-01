<template>
  <n-card class="chat-card" title="PoliSage 智能问答">
    <!-- 对话历史 -->
    <div class="history">
      <div v-for="msg in history" :key="msg.id" :class="['msg', msg.role]">
        <div class="avatar">{{ msg.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="content">
          <div v-if="msg.role === 'bot'">
            <p>{{ msg.answer }}</p>
            <!-- 渲染引用片段中的图片和文本 -->
            <div v-if="msg.reference && msg.reference.length" class="refs">
              <div v-for="(ref, idx) in msg.reference" :key="idx" class="ref-item">
                <img v-if="ref.img_path" :src="ref.img_path" alt="ref image" />
                <p v-else>{{ ref.text }}</p>
              </div>
            </div>
            <!-- 评分按钮 -->
            <n-space size="small">
              <span>评价：</span>
              <n-button v-for="n in 5" :key="n" size="small" :type="feedback[msg.id] === n ? 'primary' : 'default'"
                @click="rate(msg.id, n)">{{ n }}</n-button>
            </n-space>
          </div>
          <div v-else>
            <p>{{ msg.question }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区 -->
    <div class="input-area">
      <n-input v-model:value="inputQuestion" type="textarea" placeholder="请输入您的问题…" rows="2"
        @keydown.enter.prevent="send" />
      <n-button type="primary" :disabled="!inputQuestion.trim() || loading" @click="send">发送</n-button>
    </div>
  </n-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { NCard, NInput, NButton, NSpace } from 'naive-ui'
import { queryChat, sendFeedback } from '@/api/chat'

const history = ref([])        // { id, role, question?, answer?, reference? }
const feedback = reactive({})  // { [question_id]: rating }
const inputQuestion = ref('')
const loading = ref(false)
// 新增：记录上一次的 question_id
const previousId = ref(null)

async function send() {
  if (!inputQuestion.value.trim()) return
  loading.value = true

  // 1. 推入用户消息
  history.value.push({
    id: String(Date.now()),
    role: 'user',
    question: inputQuestion.value
  })

  try {
    // 2. 带上 previousId 调用后端
    const res = await queryChat(inputQuestion.value, previousId.value)
    const { question_id, answer, reference } = res.data

    // 3. 推入机器人回答
    history.value.push({
      id: question_id,
      role: 'bot',
      answer,
      reference: reference || []
    })

    // 4. 更新 previousId，为下次对话做上下文关联
    previousId.value = question_id

  } catch (err) {
    console.error(err)
    history.value.push({
      id: String(Date.now()),
      role: 'bot',
      answer: '出错了，请稍后再试。'
    })
  } finally {
    inputQuestion.value = ''
    loading.value = false
  }
}

function rate(question_id, rating) {
  feedback[question_id] = rating
  sendFeedback(question_id, rating)
}
</script>

<style scoped>
.chat-card {
  width: 80vw;
  max-width: 800px;
  margin: 2rem auto;
  display: flex;
  flex-direction: column;
  height: 80vh;
}

.history {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.msg {
  display: flex;
  margin-bottom: 1rem;
}

.msg.user .avatar {
  color: #409eff;
}

.msg.bot .avatar {
  color: #198754;
}

.avatar {
  width: 2rem;
  text-align: center;
  font-size: 1.5rem;
  margin-right: 0.5rem;
}

/* .content {
  flex: 1;
} */

/* .content p {
  white-space: pre-wrap;
} */

.refs {
  margin-top: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.ref-item {
  border: 1px solid #eaeaea;
  padding: 0.5rem;
  border-radius: 4px;
}

.ref-item img {
  max-width: 100px;
  max-height: 80px;
}

.input-area {
  display: flex;
  padding: 1rem;
  border-top: 1px solid #eaeaea;
}

.input-area .n-input {
  flex: 1;
  margin-right: 1rem;
}
</style>
