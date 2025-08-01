<template>
  <n-card class="my-card" title="">
    <div class="actions mb-4">
      <div class="p-4 max-w-xl mx-auto">
        <!-- 上传文件部分 -->
        <input type="file" accept="application/all" multiple @change="onFileChange" />
        <!-- 确认上传按钮 -->
        <button class="mt-2 px-4 py-2 rounded shadow bg-blue-500 text-white" :disabled="!files.length || loading"
          @click="uploadAll">
          {{ loading ? '上传中…' : '上传全部' }}
        </button>

        <div v-if="message" class="mt-4 text-green-600">{{ message }}</div>
        <n-button @click="batchDownloadAll" :disabled="!hasSelection">下载勾选</n-button>
        <n-button type="primary" :disabled="!hasJsonSelection || loadingSmart" @click="onSmartRecognize">
          {{ loadingSmart ? '识图中…' : '智能识图' }}</n-button>
        <n-button @click="batchDelete" type="error" :disabled="!hasSelection">批量删除</n-button>
        <n-button @click="selectAll">全选</n-button>
        <n-button @click="invertSelect">反选</n-button>
      </div>
    </div>

    <n-data-table :columns="columns" :data="sortedDocs" :row-key="rowKey" v-model:checked-row-keys="checkedKeys"
      class="w-full" />
    <!-- 编辑弹窗 -->
    <n-modal v-model:show="showEditModal" title="编辑 JSON 文本字段" preset="dialog" style="width: 70vw;">
      <div v-for="(item, idx) in editJson" :key="idx" class="mb-6 p-4 border rounded">
        <div class="mb-2 font-bold">对象 {{ idx + 1 }}（type: {{ item.type }}）</div>
        <!-- 展示除 text 外的其他字段只读 -->
        <pre class="bg-gray-100 p-2 rounded mb-2">{{
          // 组合显示其他字段
          Object.fromEntries(Object.entries(item).filter(([k]) => k !== 'text'))
        }}</pre>
        <!-- 可编辑的 text 字段 -->
        <n-input type="textarea" v-model:value="editJson[idx].text" rows="3" placeholder="编辑 text 内容" />
      </div>
      <template #action>
        <n-button @click="showEditModal = false">取消</n-button>
        <n-button type="primary" @click="saveEdit">提交</n-button>
      </template>
    </n-modal>
  </n-card>
</template>

<script setup>
import { ref, reactive, computed, onMounted, h, nextTick } from 'vue'
import { NCard, NButton, NDataTable, NCheckbox, NSpace } from 'naive-ui'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import { uploadFiles, fetchDocs, deleteDocs, modifyJson, intelligentRecognize } from '@/api/file'

// State
const files = ref([])
const loading = ref(false)
const message = ref('')
const docsOriginal = ref([])  // 原始顺序
const checkedKeys = ref([])

const editingRow = ref(null)
const originalJson = ref([])   // 存原始 JSON 数组
const editJson = reactive([])  // 可编辑的深拷贝
const showEditModal = ref(false)
const loadingSmart = ref(false)

// Sorting state
const sortKey = ref(null)
const sortOrder = ref(null)       // 'asc' | 'desc' | null
const sortedDocs = computed(() => { // Compute displayed docs
  const arr = docsOriginal.value.slice()
  if (!sortKey.value || !sortOrder.value) {
    return arr
  }
  return arr.sort((a, b) => {
    let valA = a[sortKey.value]
    let valB = b[sortKey.value]
    // parse sizes if sorting size
    if (sortKey.value === 'pdf_size') {
      const toNum = s => parseFloat(s)
      valA = toNum(valA)
      valB = toNum(valB)
    }
    if (valA < valB) return sortOrder.value === 'asc' ? -1 : 1
    if (valA > valB) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
})

// Toggle sort cycle: null -> asc -> desc -> null
function changeSort(key) {
  if (sortKey.value !== key) {
    sortKey.value = key
    sortOrder.value = 'asc'
  } else {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : sortOrder.value === 'desc' ? null : 'asc'
    if (!sortOrder.value) sortKey.value = null
  }
}

const hasSelection = computed(() => checkedKeys.value.length > 0)
const hasJsonSelection = computed(() => {
  return checkedKeys.value.some(key => {
    const row = docsOriginal.value.find(d => d.file_name === key)
    return row && row.file_type === 'json'
  })
})

function rowKey(row) {
  return row.file_name
}

// Columns with sort icons
const columns = [
  { type: 'selection', title: '勾选', width: '8px' },
  {
    key: 'actions',
    title: '编辑',
    width: 80,
    render: row => h(
      NSpace,
      {},
      {
        default: () => row.file_type === 'json'
          ? h(
            NButton,
            { size: 'small', onClick: () => onEditJson(row) },
            { default: () => '编辑' }
          )
          : null
      }
    )
  },
  {
    key: 'file_name',
    title: () => h('div', {
      style: { display: 'flex', alignItems: 'center', cursor: 'pointer' },
      onClick: () => changeSort('file_name')
    }, [
      '名称 ',
      sortIcon('file_name')
    ]), render: row => h('a', { href: row.json_url || row.image_url, target: '_blank', rel: 'noopener' }, row.file_name),
    width: '120px'
  },
  {
    key: 'file_type',
    title: () => h('div', {
      style: { display: 'flex', alignItems: 'center', cursor: 'pointer' },
      onClick: () => changeSort('file_type')
    }, [
      '类型 ',
      sortIcon('file_type')
    ]),
    width: '49px'
  },
  {
    key: 'file_size',
    title: () => h('div', {
      style: { display: 'flex', alignItems: 'center', cursor: 'pointer' },
      onClick: () => changeSort('file_size')
    }, [
      '体积 ',
      sortIcon('file_size')
    ]),
    width: '49px'
  },
  {
    key: 'upload_time',
    title: () => h('div', {
      style: { display: 'flex', alignItems: 'center', cursor: 'pointer' },
      onClick: () => changeSort('upload_time')
    }, [
      '时间 ',
      sortIcon('upload_time')
    ]),
    width: '80px'
  }
]

function sortIcon(key) {
  if (sortKey.value !== key) return '↕'
  return sortOrder.value === 'asc' ? '▲' : sortOrder.value === 'desc' ? '▼' : '↕'
}

function selectAll() { checkedKeys.value = docsOriginal.value.map(d => d.file_name) }
function invertSelect() {
  const all = docsOriginal.value.map(d => d.file_name)
  checkedKeys.value = all.filter(k => !checkedKeys.value.includes(k))
}

// Load docs
async function load() {
  try {
    const res = await fetchDocs()
    docsOriginal.value = res.data
  } catch (e) {
    console.error('加载文件列表失败', e)
  }
}

onMounted(load)
// 上传文件的函数
function onFileChange(e) {
  files.value = Array.from(e.target.files)
}

// Batch upload
async function uploadAll() {
  if (!files.value.length) return alert('请先选择至少一个 PDF')
  loading.value = true; message.value = ''
  try {
    const form = new FormData(); files.value.forEach(f => form.append('files', f))
    const { data } = await uploadFiles(form)
    message.value = `上传成功：${data.map(i => i.file_name).join('，')}`
    setTimeout(load, 1000)
  } catch { alert('上传失败') } finally { loading.value = false }
}

async function addToZip(zipOrFolder, urlKey, nameKey, row, includeFolder = true) {
  // 确定目标容器：zip 根或子文件夹
  const container = includeFolder && zipOrFolder.folder
    ? zipOrFolder.folder(row.file_name.replace(/\.[^.]+$/, ''))
    : zipOrFolder

  try {
    const res = await fetch(row[urlKey])
    if (res.ok) {
      const blob = await res.blob()
      container.file(row[nameKey], blob)
    }
  } catch (e) {
    console.warn(`下载 ${row[nameKey]} 失败`, e)
  }
}

async function batchDownloadAll() {
  // 1. 筛选出被勾选的行
  const selected = docsOriginal.value.filter(
    d => checkedKeys.value.includes(d.file_name)
  )
  if (!selected.length) return alert('请先勾选至少一个文件')
  // 2. 创建一个新的 ZIP 实例
  const zip = new JSZip()
  // 3. 遍历每一行，分别下载 json 和 image（如果存在），直接放在压缩包根目录
  for (const row of selected) {
    if (row.json_url) {
      await addToZip(zip, 'json_url', 'file_name', row, false)
    }
    if (row.image_url) {
      await addToZip(zip, 'image_url', 'file_name', row, false)
    }
  }
  // 4. 生成 ZIP 二进制并保存
  try {
    const content = await zip.generateAsync({ type: 'blob' })
    saveAs(content, 'all_files.zip')
  } catch (e) {
    console.error('打包失败', e)
    alert('下载失败，请稍后重试')
  }
}

async function batchDelete() {
  if (!confirm('删除?')) return;
  await Promise.all(docsOriginal.value.filter(
    d => checkedKeys.value.includes(d.file_name))
    .map(r => deleteDocs(r.file_name))); load()
}

async function onEditJson(row) {
  const res = await fetch(row.json_url)
  const data = await res.json()            // 这是一个数组
  editingRow.value = row
  originalJson.value = data
  // 深拷贝，并只保留需要编辑的 text 字段，其它字段也保留用于显示
  editJson.splice(0, editJson.length, ...data.map(item => ({ ...item })))
  showEditModal.value = true
}

async function onSmartRecognize() {
  if (!hasJsonSelection.value) return
  loadingSmart.value = true
  try {
    // 1. 找到所有被选且 file_type=json 的行
    const targets = docsOriginal.value.filter(
      d => checkedKeys.value.includes(d.file_name) && d.file_type === 'json'
    )

    // 2. 并行调用后端接口
    await Promise.all(
      targets.map(row =>
        intelligentRecognize(row.file_name)
      )
    )

    // 3. 提示与刷新
    alert(`已对 ${targets.length} 个 JSON 文件完成智能识图`)
    await load()  // 重新拉取最新列表（如果后端有生成新字段、URL 等）
  } catch (err) {
    console.error('智能识图出错', err)
    alert('智能识图失败，请稍后重试')
  } finally {
    loadingSmart.value = false
  }
}

// 保存修改
async function saveEdit() {
  try {
    // editJson 已经是包含修改后 text 的完整数组
    await modifyJson(editingRow.value.file_name, editJson)
    showEditModal.value = false
    editingRow.value = null
    await load()  // 刷新列表
    alert('修改成功')
  } catch (err) {
    console.error(err)
    alert('保存失败，请检查网络或 JSON 格式')
  }
}
</script>

<style scoped>
.my-card {
  min-width: 1000px;
}
</style>
