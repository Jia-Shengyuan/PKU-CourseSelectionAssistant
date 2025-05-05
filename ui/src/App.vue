<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 配置信息
const formData = reactive({
  studentId: '',
  password: '',
  grade: '',
  userDescription: '',
  apiProvider: 'https://api.siliconflow.cn/v1/',
  modelName: 'deepseek-ai/DeepSeek-V3',
  apiKey: '',
  temperature: 0.7,
  topP: 0.9,
  stream: true
})

// 课程列表数据
const courses = ref([
  {
    name: '高等数学',
    classes: [
      {
        id: 1,
        teacher: '张老师',
        time: '周一 1-2节',
        location: '理教101'
      },
      {
        id: 2,
        teacher: '李老师',
        time: '周二 3-4节',
        location: '理教102'
      }
    ]
  },
  {
    name: '大学物理',
    classes: [
      {
        id: 3,
        teacher: '王老师',
        time: '周三 3-4节',
        location: '理教201'
      }
    ]
  }
])

// 添加课程对话框
const addCourseDialogVisible = ref(false)
const newCourse = reactive({
  name: '',
  classes: [{
    id: '',
    teacher: '',
    time: '',
    location: ''
  }]
})

// 编辑课程对话框
const editCourseDialogVisible = ref(false)
const editingCourseIndex = ref(-1)
const editingClassIndex = ref(-1)
const editingCourse = reactive({
  name: '',
  classes: [{
    id: '',
    teacher: '',
    time: '',
    location: ''
  }]
})

const activeNames = ref([]) // 控制折叠面板的展开状态
const coursePreference = ref('') // 选课倾向
const minCredits = ref(0) // 最少学分
const maxCredits = ref(0) // 最多学分

// 处理最低学分变化
const handleMinCreditsChange = (value) => {
  if (value > maxCredits.value) {
    maxCredits.value = value
  }
}

// 处理最高学分变化
const handleMaxCreditsChange = (value) => {
  if (value < minCredits.value) {
    minCredits.value = Math.max(0, value)
  }
}

// 显示添加课程对话框
const showAddCourseDialog = () => {
  addCourseDialogVisible.value = true
  // 清空表单
  newCourse.name = ''
  newCourse.classes = [{
    id: '',
    teacher: '',
    time: '',
    location: ''
  }]
}

// 显示编辑课程对话框
const showEditCourseDialog = (courseIndex, classIndex) => {
  editingCourseIndex.value = courseIndex
  editingClassIndex.value = classIndex
  const course = courses.value[courseIndex]
  const classInfo = course.classes[classIndex]
  editingCourse.name = course.name
  editingCourse.classes = [{
    id: classInfo.id,
    teacher: classInfo.teacher,
    time: classInfo.time,
    location: classInfo.location
  }]
  editCourseDialogVisible.value = true
}

// 添加课程（如"数学分析"）
const addCourse = () => {
  if (!newCourse.name) {
    ElMessage.warning('请输入课程名称')
    return
  }
  // 自动添加一个样例班级
  const newId = Math.max(...courses.value.flatMap(c => c.classes.map(cl => cl.id)), 0) + 1
  courses.value.push({
    name: newCourse.name,
    classes: [{
      id: newId,
      teacher: '待设置',
      time: '待设置',
      location: '待设置'
    }]
  })
  addCourseDialogVisible.value = false
  ElMessage.success('添加成功')
}

// 添加班级（如"高等数学 王老师班"）
const addClass = (courseIndex) => {
  const course = courses.value[courseIndex]
  const newId = Math.max(...course.classes.map(c => c.id), 0) + 1
  // 打开编辑对话框
  editingCourseIndex.value = courseIndex
  editingClassIndex.value = course.classes.length
  editingCourse.name = course.name
  editingCourse.classes = [{
    id: newId,
    teacher: '',
    time: '',
    location: ''
  }]
  editCourseDialogVisible.value = true
}

// 编辑班级
const editClass = () => {
  if (!editingCourse.name || !editingCourse.classes[0].id) {
    ElMessage.warning('请输入课程编号和教师信息')
    return
  }
  const courseIndex = editingCourseIndex.value
  const classIndex = editingClassIndex.value
  const course = courses.value[courseIndex]
  
  // 如果是新添加的班级
  if (classIndex === course.classes.length) {
    course.classes.push({ ...editingCourse.classes[0] })
    // 自动展开该课程
    if (!activeNames.value.includes(courseIndex)) {
      activeNames.value.push(courseIndex)
    }
  } else {
    course.classes[classIndex] = { ...editingCourse.classes[0] }
  }
  
  editCourseDialogVisible.value = false
  ElMessage.success('编辑成功')
}

// 删除课程
const deleteCourse = (courseIndex) => {
  ElMessageBox.confirm(
    `确定要删除课程"${courses.value[courseIndex].name}"及其所有班级吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    courses.value.splice(courseIndex, 1)
    ElMessage.success('删除成功')
  }).catch(() => {
    // 用户取消删除，不做任何操作
  })
}

// 删除班级
const deleteClass = (courseIndex, classIndex) => {
  const course = courses.value[courseIndex]
  course.classes.splice(classIndex, 1)
  if (course.classes.length === 0) {
    courses.value.splice(courseIndex, 1)
  }
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
  const courseName = file.name.split('.')[0]
  const newId = courses.value.length + 1
  courses.value.push({
    name: courseName,
    classes: [{
      id: newId,
      teacher: '待设置',
      time: '待设置',
      location: '待设置'
    }]
  })
  ElMessage.success(`成功导入培养方案：${courseName}`)
}

// 保存选课倾向
const savePreference = () => {
  ElMessage.success('保存成功')
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
              <el-input v-model="formData.grade" placeholder="请输入年级（如大一下）" />
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
                placeholder="您可以在此进行自我介绍，帮助大模型更好地了解您"
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
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="温度">
              <el-slider
                v-model="formData.temperature"
                :min="0"
                :max="1"
                :step="0.01"
                :format-tooltip="value => value.toFixed(2)"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Top P">
              <el-slider
                v-model="formData.topP"
                :min="0"
                :max="1"
                :step="0.01"
                :format-tooltip="value => value.toFixed(2)"
              />
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
      <el-collapse v-model="activeNames" class="course-collapse">
        <el-collapse-item v-for="(course, courseIndex) in courses" :key="courseIndex" :name="courseIndex">
          <template #title>
            <div class="collapse-title">
              <span>{{ course.name }}</span>
              <div class="button-group">
                <el-button type="primary" size="small" @click.stop="addClass(courseIndex)">
                  添加班级
                </el-button>
                <el-button type="danger" size="small" @click.stop="deleteCourse(courseIndex)">
                  删除课程
                </el-button>
              </div>
            </div>
          </template>
          <el-table :data="course.classes" style="width: 100%">
            <el-table-column prop="id" label="课程编号" width="100" />
            <el-table-column prop="teacher" label="教师" />
            <el-table-column prop="time" label="上课时间" />
            <el-table-column prop="location" label="上课地点" />
            <el-table-column label="操作" width="200">
          <template #default="scope">
                <el-button type="primary" size="small" @click="showEditCourseDialog(courseIndex, scope.$index)">
              编辑
            </el-button>
                <el-button type="danger" size="small" @click="deleteClass(courseIndex, scope.$index)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <el-card class="preference-card">
      <template #header>
        <div class="card-header">
          <span>选课倾向</span>
        </div>
      </template>
      <div class="preference-content">
        <div class="credits-input">
          <el-form-item label="最低学分">
            <el-input-number 
              v-model="minCredits" 
              :min="0" 
              :max="100"
              @change="handleMinCreditsChange"
            />
          </el-form-item>
          <el-form-item label="最高学分">
            <el-input-number 
              v-model="maxCredits" 
              :min="0" 
              :max="100"
              @change="handleMaxCreditsChange"
            />
          </el-form-item>
        </div>
        <el-input
          v-model="coursePreference"
          type="textarea"
          :rows="4"
          placeholder="请描述您的选课倾向，例如：希望课程时间分布均匀，避免连续上课；优先选择教学经验丰富的老师；对课程难度没有特别要求等"
        />
      </div>
    </el-card>

    <div class="button-container">
      <el-button type="success" size="large" @click="savePreference">保存</el-button>
      <el-button type="primary" size="large" @click="handleConfirm">开始搜索推荐</el-button>
    </div>

    <!-- 添加课程对话框 -->
    <el-dialog v-model="addCourseDialogVisible" title="添加课程" width="500px">
      <el-form :model="newCourse" label-width="80px">
        <el-form-item label="课程名称">
          <el-input v-model="newCourse.name" placeholder="请输入课程名称" />
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
          <el-input v-model="editingCourse.name" disabled />
        </el-form-item>
        <el-form-item label="课程编号">
          <el-input v-model.number="editingCourse.classes[0].id" type="number" />
        </el-form-item>
        <el-form-item label="教师">
          <el-input v-model="editingCourse.classes[0].teacher" />
        </el-form-item>
        <el-form-item label="上课时间">
          <el-input v-model="editingCourse.classes[0].time" />
        </el-form-item>
        <el-form-item label="上课地点">
          <el-input v-model="editingCourse.classes[0].location" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editCourseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="editClass">确定</el-button>
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
  min-height: 100vh;
}

#app {
  width: 100%;
  min-height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>

<style scoped>
.app-container {
  width: 90%;
  max-width: 1200px;
  min-width: 800px;
  margin: 20px auto;
  padding: 20px;
  min-height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
}

.config-card,
.course-card,
.preference-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  flex: 1;
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
  gap: 20px;
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

.course-collapse {
  margin-top: 20px;
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: 600;
}

:deep(.el-collapse-item__content) {
  padding: 20px;
}

.collapse-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 20px;
}

.collapse-title .button-group {
  display: flex;
  gap: 10px;
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: 600;
  padding-right: 20px;
}

.preference-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.preference-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.credits-input {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
}

.credits-input :deep(.el-form-item) {
  margin-bottom: 0;
}

.credits-input :deep(.el-input-number) {
  width: 120px;
}

:deep(.el-slider) {
  margin-top: 8px;
}

:deep(.el-slider__runway) {
  margin: 16px 0;
}
</style>