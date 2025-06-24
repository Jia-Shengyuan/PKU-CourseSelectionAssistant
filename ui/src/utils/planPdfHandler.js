import { ElMessage } from 'element-plus'
import { uploadPlanPdf } from '@/api/course'

/**
 * 处理培养方案PDF上传
 * @param {Event} event - 文件输入事件
 * @returns {Promise<void>}
 */
export const handlePlanPdfUpload = async (event) => {

  const file = event.target.files[0]
  if (!file) return
  
  if (file.type !== 'application/pdf') {
    ElMessage.error('请选择PDF格式的文件')
    return
  }
  
  try {
    ElMessage.info('正在上传培养方案PDF...')
    await uploadPlanPdf(file)
    ElMessage.success('培养方案PDF上传成功，您可以点击"导入培养方案课程"按钮导入课程')
  } catch (error) {
    console.error('上传培养方案PDF失败:', error)
    ElMessage.error('上传培养方案PDF失败，请重试')
  }
  
  // 重置文件输入以允许重新选择同一文件
  event.target.value = ''
}
