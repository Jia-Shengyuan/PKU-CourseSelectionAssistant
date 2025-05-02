<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// 配置信息
const formData = reactive({
  studentId: '',
  password: '',
  grade: '',
  userDescription: '',
  apiProvider: 'https://api.siliconflow.cn/v1/',
  modelName: 'deepseek-ai/DeepSeek-V3',
  apiKey: ''
})

// 课程列表数据
const courses = ref([
  {
    name: '高等数学',
    teacher: '张老师',
    time: '周一 1-2节',
    location: '理教101'
  },
  {
    name: '大学物理',
    teacher: '李老师',
    time: '周三 3-4节',
    location: '理教201'
  },
  {
    name: '计算机导论',
    teacher: '王老师',
    time: '周五 5-6节',
    location: '理教301'
  }
])

// 添加课程对话框
const addCourseDialogVisible = ref(false)
const newCourse = reactive({
  name: '',
  teacher: '',
  time: '',
  location: ''
})

// 编辑课程对话框
const editCourseDialogVisible = ref(false)
const editingCourseIndex = ref(-1)
const editingCourse = reactive({
  name: '',
  teacher: '',
  time: '',
  location: ''
})

// 显示添加课程对话框
const showAddCourseDialog = () => {
  addCourseDialogVisible.value = true
  // 清空表单
  Object.keys(newCourse).forEach(key => {
    newCourse[key] = ''
  })
}

// 显示编辑课程对话框
const showEditCourseDialog = (index) => {
  editingCourseIndex.value = index
  const course = courses.value[index]
  editingCourse.name = course.name
  editingCourse.teacher = course.teacher
  editingCourse.time = course.time
  editingCourse.location = course.location
  editCourseDialogVisible.value = true
}

// 添加课程
const addCourse = () => {
  if (!newCourse.name) {
    ElMessage.warning('请输入课程名称')
    return
  }
  courses.value.push({ ...newCourse })
  addCourseDialogVisible.value = false
  ElMessage.success('添加成功')
}

// 编辑课程
const editCourse = () => {
  if (!editingCourse.name) {
    ElMessage.warning('请输入课程名称')
    return
  }
  courses.value[editingCourseIndex.value] = { ...editingCourse }
  editCourseDialogVisible.value = false
  ElMessage.success('编辑成功')
}

// 删除课程
const deleteCourse = (index) => {
  courses.value.splice(index, 1)
  ElMessage.success('删除成功')
}

// 确认按钮点击事件
const handleConfirm = () => {
  if (!formData.studentId || !formData.password) {
    ElMessage.warning('请填写学号和密码')
    return
  }
  if (courses.value.length === 0) {
    ElMessage.warning('请至少添加一门课程')
    return
  }
  // TODO: 实现搜索推荐逻辑
  console.log('开始搜索推荐', formData, courses.value)
}

// 处理文件导入
const handleFileImport = (file) => {
  // 暂时只使用文件名作为课程名
  const courseName = file.name.split('.')[0] // 去掉文件扩展名
  courses.value.push({
    name: courseName,
    teacher: '待设置',
    time: '待设置',
    location: '待设置'
  })
  ElMessage.success(`成功导入培养方案：${courseName}`)
}
</script>

<template>
  <div class="app-container">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>配置信息</span>
        </div>
      </template>
      <el-form :model="formData" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="学号">
              <el-input v-model="formData.studentId" placeholder="请输入学号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="门户密码">
              <el-input v-model="formData.password" type="password" placeholder="请输入密码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="年级">
              <el-input v-model="formData.grade" placeholder="请输入年级" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24">
            <el-form-item label="用户自述">
              <el-input
                v-model="formData.userDescription"
                type="textarea"
                :rows="3"
                placeholder="请输入您的选课需求和偏好"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="API提供商">
              <el-input v-model="formData.apiProvider" placeholder="请输入大模型API提供网站链接" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="模型名称">
              <el-input v-model="formData.modelName" placeholder="请输入大模型名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="API密钥">
              <el-input v-model="formData.apiKey" type="password" placeholder="请输入API密钥" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="course-card">
      <template #header>
        <div class="card-header">
          <span>课程列表</span>
          <div class="button-group">
            <el-upload
              class="upload-demo"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              @change="handleFileImport"
            >
              <el-button type="success">导入培养方案</el-button>
            </el-upload>
            <el-button type="primary" @click="showAddCourseDialog">手动添加课程</el-button>
          </div>
        </div>
      </template>
      <el-table :data="courses" style="width: 100%">
        <el-table-column prop="name" label="课程名称" width="180" />
        <el-table-column prop="teacher" label="教师" width="120" />
        <el-table-column prop="time" label="上课时间" width="180" />
        <el-table-column prop="location" label="上课地点" width="180" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="primary" size="small" @click="showEditCourseDialog(scope.$index)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="deleteCourse(scope.$index)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <div class="button-container">
      <el-button type="primary" size="large" @click="handleConfirm">开始搜索推荐</el-button>
    </div>

    <!-- 添加课程对话框 -->
    <el-dialog v-model="addCourseDialogVisible" title="添加课程" width="500px">
      <el-form :model="newCourse" label-width="80px">
        <el-form-item label="课程名称">
          <el-input v-model="newCourse.name" />
        </el-form-item>
        <el-form-item label="教师">
          <el-input v-model="newCourse.teacher" />
        </el-form-item>
        <el-form-item label="上课时间">
          <el-input v-model="newCourse.time" />
        </el-form-item>
        <el-form-item label="上课地点">
          <el-input v-model="newCourse.location" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addCourseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addCourse">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑课程对话框 -->
    <el-dialog v-model="editCourseDialogVisible" title="编辑课程" width="500px">
      <el-form :model="editingCourse" label-width="80px">
        <el-form-item label="课程名称">
          <el-input v-model="editingCourse.name" />
        </el-form-item>
        <el-form-item label="教师">
          <el-input v-model="editingCourse.teacher" />
        </el-form-item>
        <el-form-item label="上课时间">
          <el-input v-model="editingCourse.time" />
        </el-form-item>
        <el-form-item label="上课地点">
          <el-input v-model="editingCourse.location" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editCourseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="editCourse">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  background-color: #f5f7fa;
}

#app {
  width: 100%;
  min-height: 100vh;
  background-color: #f5f7fa;
}
</style>

<style scoped>
.app-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
  min-height: 100vh;
}

.config-card,
.course-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.button-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-card__header) {
  padding: 15px 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-table) {
  border-radius: 4px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-table td) {
  padding: 12px 0;
}

:deep(.el-button--primary) {
  background-color: #409eff;
  border-color: #409eff;
}

:deep(.el-button--primary:hover) {
  background-color: #66b1ff;
  border-color: #66b1ff;
}

:deep(.el-button--danger) {
  background-color: #f56c6c;
  border-color: #f56c6c;
}

:deep(.el-button--danger:hover) {
  background-color: #f78989;
  border-color: #f78989;
}

:deep(.el-input__inner) {
  border-radius: 4px;
}

:deep(.el-textarea__inner) {
  border-radius: 4px;
  min-height: 100px !important;
}

.button-group {
  display: flex;
  gap: 10px;
}
</style>
