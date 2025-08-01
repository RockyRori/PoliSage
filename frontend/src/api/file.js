import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL
})

// 批量上传 json 文件接口
export function uploadFiles(formData) {
    return api.post('/files/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    })
}

// 获取文件列表
export function fetchDocs() {
    return api.get('/files')
}

// 批量删除文档接口
export function deleteDocs(file_name) {
    const name = encodeURIComponent(file_name)
    return api.delete(`/files/${name}`)
}

export function intelligentRecognize(file_name) {
    return api.post(`/files/${file_name}/generate_captions`)
}

export function modifyJson(fileName, content) {
    const name = encodeURIComponent(fileName)
    return api.put(`/files/${name}`, { content })
}
