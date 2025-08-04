import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
})

/**
 * 向后端发送用户问题，获取回答
 * @param {string} question     用户输入的问题
 * @param {string|null} previousId  上一个提问的 ID（首次可传 null 或空字符串）
 * @returns Promise<{ question_id: string, answer: string }>
 */
export function queryChat(question, previousId = null) {
  return api.post('/chat/query', {
    question,
    previous_id: previousId,
    model: "default",
    language: "Chinese"
  })
}

/**
 * 将用户对回答的评分和备注反馈给后端
 * @param {string} question_id
 * @param {number} rating
 * @param {string} [comments]
 */
export function sendFeedback(question_id, rating, comments = '') {
  return api.post('/chat/feedback', { question_id, rating, comments })
}
