<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { fetchCourseRawInfo, fetchCourse, fetchCourseByPlan, courseDataToMapArray, activateDatabase, getCourseEvaluation, readPlanPDF, genPlan } from '@/api/course'
import { getConfig, saveConfig } from '@/api/config'
import { loginTreehole, searchTreehole } from '@/api/crawler'
import { generateTableData } from '@/api/timetable'
import { savePreference } from '@/utils/configService'

// 配置信息
const formData = reactive({
  studentId: '',
  password: '',
  grade: '',
  semester: '',
  userDescription: '',
  apiProvider: 'https://api.siliconflow.cn/v1/',
  modelName: 'deepseek-ai/DeepSeek-V3',
  apiKey: '',
  temperature: 0.7,
  topP: 0.9,
  stream: true,
  chrome_user_data_dir: 'config/chrome_data',
  num_timetable: 1,
  num_search: 5,
  sleep_after_search: 5,
  sleep_between_scroll: 0.5,
  sleep_random_range: 0.1
})

// 存储原有学期
const originalSemester = ref('')
// 记录数据库是否已激活
const isDatabaseActivated = ref(false)

// 课程列表数据
const courses = ref([])

// 添加课程对话框
const addCourseDialogVisible = ref(false)
const newCourse = reactive({
  name: '',
  teacher: '',
  class_id: ''
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

// 添加班级对话框
const addClassDialogVisible = ref(false)
const addingCourseIndex = ref(-1)
const newClass = reactive({
  class_id: '',
  teacher: ''
})

// 计算当前正在添加班级的课程名称
const addingCourseName = computed(() => {
  return courses.value[addingCourseIndex.value]?.name || ''
})

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
  newCourse.class_id = ''
  newCourse.teacher = ''
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
const addCourse = async () => {
  if (!isDatabaseActivated.value) {
    ElMessage.warning('请先设置学期，并激活数据库')
    return
  }

  if (!newCourse.name) {
    ElMessage.warning('请输入课程名称')
    return
  }

  // 检查课程是否已存在
  if (courses.value.some(course => course.name === newCourse.name)) {
    ElMessage.warning(`课程"${newCourse.name}"已存在`)
    return
  }

  try {
    // 从API获取课程信息
    const courseData = await fetchCourse(
      newCourse.name,
      newCourse.class_id ? parseInt(newCourse.class_id) : null,
      newCourse.teacher || null
    )
    
    if (!courseData || courseData.length === 0) {
      ElMessage.warning(`未找到课程"${newCourse.name}"的信息`)
      return
    }

    // 将API返回的数据转换为前端需要的格式
    const newCourseData = {
      name: newCourse.name,
      classes: courseData.map(course => ({
        id: course.class_id.toString(),
        teacher: course.teacher,
        time: course.time,
        location: course.location
      }))
    }

    // 添加到课程列表
    courses.value.push(newCourseData)
    
    // 自动展开新添加的课程
    const newIndex = courses.value.length - 1
    if (!activeNames.value.includes(newIndex)) {
      activeNames.value.push(newIndex)
    }

    addCourseDialogVisible.value = false
    ElMessage.success(`成功添加课程"${newCourse.name}"，包含${courseData.length}个班级`)
  } catch (error) {
    console.error('添加课程失败:', error)
    ElMessage.error('添加课程失败')
  }
}

// 添加班级（如"高等数学 王老师班"）
const addClass = (courseIndex) => {
  addingCourseIndex.value = courseIndex
  // 清空表单
  newClass.class_id = ''
  newClass.teacher = ''
  addClassDialogVisible.value = true
}

// 确认添加班级
const confirmAddClass = async () => {
  const course = courses.value[addingCourseIndex.value]
  
  try {
    // 从API获取课程信息
    const courseData = await fetchCourse(
      course.name,
      newClass.class_id ? parseInt(newClass.class_id) : null,
      newClass.teacher || null
    )
    
    if (!courseData || courseData.length === 0) {
      ElMessage.warning('未找到匹配的班级信息')
      return
    }

    // 过滤掉已存在的班级
    const newClasses = courseData.filter(courseInfo => 
      !course.classes.some(c => 
        c.id === courseInfo.class_id.toString() || c.teacher === courseInfo.teacher
      )
    )

    if (newClasses.length === 0) {
      ElMessage.warning('所有匹配的班级都已存在')
      return
    }

    // 添加新班级
    course.classes.push(...newClasses.map(courseInfo => ({
      id: courseInfo.class_id.toString(),
      teacher: courseInfo.teacher,
      time: courseInfo.time,
      location: courseInfo.location
    })))

    // 自动展开该课程
    if (!activeNames.value.includes(addingCourseIndex.value)) {
      activeNames.value.push(addingCourseIndex.value)
    }

    addClassDialogVisible.value = false
    ElMessage.success(`成功添加${newClasses.length}个班级`)
  } catch (error) {
    console.error('添加班级失败:', error)
    ElMessage.error('添加班级失败')
  }
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

// 课程评价状态
const courseEvaluationStatus = ref({})  // 存储每个课程的评价状态
const courseEvaluationContent = ref({})  // 存储每个课程的评价内容
const activeEvaluationTab = ref('')  // 当前激活的评价标签页

// 课程评价状态枚举
const EvaluationStatus = {
  QUEUED: '队列中',
  SEARCHING: '搜索中',
  EVALUATING: '评价中',
  COMPLETED: '已完成'
}

const timetables = ref([]) // 存储所有课表
const activeTimetableIndex = ref(0) // 当前显示的课表索引

const handleCourseEvaluation = async () => {
  if (courses.value.length === 0) {
    ElMessage.warning('请至少添加一门课程')
    return
  }

  try {
    // 先登录树洞
    ElMessage.info('正在登录树洞...')
    await loginTreehole()
    ElMessage.success('登录树洞成功')

    // 初始化评价状态
    courses.value.forEach(course => {
      courseEvaluationStatus.value[course.name] = EvaluationStatus.QUEUED
      courseEvaluationContent.value[course.name] = ''
    })

    // 设置第一个标签页为激活状态
    if (courses.value.length > 0) {
      activeEvaluationTab.value = courses.value[0].name
    }

    // 创建一个队列来存储待处理的课程
    const courseQueue = [...courses.value]
    let isSearching = false

    // 处理树洞搜索的函数
    const processSearch = async (course) => {
      try {
        // 更新状态为搜索中
        courseEvaluationStatus.value[course.name] = EvaluationStatus.SEARCHING
        
        // 搜索树洞评价
        const rawText = await searchTreehole(course.name)
        
        // 更新状态为评价中
        courseEvaluationStatus.value[course.name] = EvaluationStatus.EVALUATING
        
        // 开始大模型评价（不等待完成）
        processEvaluation(course, rawText)
        
        // 继续处理队列中的下一个课程
        isSearching = false
        processQueue()
      } catch (error) {
        console.error(`搜索课程 ${course.name} 评价失败:`, error)
        ElMessage.error(`搜索课程 ${course.name} 评价失败`)
        isSearching = false
        processQueue()
      }
    }

    // 处理大模型评价的函数
    const processEvaluation = async (course, rawText) => {
      try {
        // 初始化评价内容
        courseEvaluationContent.value[course.name] = ''
        
        // 获取大模型评价（流式）
        await getCourseEvaluation(
          course.name,
          rawText,
          (chunk) => {
            // 更新评价内容
            courseEvaluationContent.value[course.name] += chunk
          }
        )
        
        // 更新状态为已完成
        courseEvaluationStatus.value[course.name] = EvaluationStatus.COMPLETED

        // 检查是否所有课程都已完成评价
        const allCompleted = courses.value.every(
          course => courseEvaluationStatus.value[course.name] === EvaluationStatus.COMPLETED
        )

        if (allCompleted) {
          // 所有课程评价完成，生成课表
          await generateTimetables()
        }
      } catch (error) {
        console.error(`评价课程 ${course.name} 失败:`, error)
        ElMessage.error(`评价课程 ${course.name} 失败`)
      }
    }

    // 处理队列中的课程
    const processQueue = async () => {
      if (isSearching || courseQueue.length === 0) {
        return
      }

      isSearching = true
      const course = courseQueue.shift()
      processSearch(course)
    }

    // 开始处理队列
    processQueue()
  } catch (error) {
    console.error('登录树洞失败:', error)
    ElMessage.error('登录树洞失败，请检查网络连接')
  }
}

// 生成课表
const generateTimetables = async () => {
  try {
    // 准备课程评价数据
    const allClasses = courses.value.map(course => ({
      course_name: course.name,
      summary: courseEvaluationContent.value[course.name],
      choices: course.classes.map(c => ({
        name: course.name,
        class_id: parseInt(c.id),
        course_id: c.course_id,
        note: c.note,
        time: c.time,
        credit: c.credit,
        teacher: c.teacher,
        location: c.location
      }))
    }))

    const plan = await readPlanPDF()

    const requestData = {
      all_classes: allClasses,
      user_description: formData.userDescription,
      plan: plan,
      class_choosing_preference: coursePreference.value,
      min_credits: minCredits.value,
      max_credits: maxCredits.value,
      num_plans: formData.num_timetable
    }

    console.log('发送的请求数据:', requestData)  // 添加日志

    const response = await genPlan(requestData)
    timetables.value = response
    activeTimetableIndex.value = 0

    ElMessage.success('课表生成成功')
  } catch (error) {
    console.error('生成课表失败:', error)
    ElMessage.error('生成课表失败')
  }
}

// 处理文件导入
const handleFileImport = async () => {

  if(!isDatabaseActivated.value) {
    ElMessage.warning('请先设置学期，并激活数据库')
    return
  }

  ElMessage.info('准备导入培养方案')

  try {
    // 获取课程列表
    const courseData = await fetchCourseByPlan(
      formData.semester,
      formData.grade,
      'config/plan.pdf' // 使用固定的培养方案路径
    )
    
    if (!courseData || courseData.length === 0) {
      ElMessage.warning('未找到课程信息')
      return
    }

    courses.value = courseDataToMapArray(courseData)
    ElMessage.success('成功导入培养方案')
   
  } catch (error) {
    console.error('导入培养方案失败:', error)
    ElMessage.error('导入培养方案失败')
  }
}

// 处理设定学期
const handleSetSemester = async () => {

  if (!formData.semester) {
    ElMessage.warning('请输入学期')
    return
  }
  
  if (formData.semester === originalSemester.value) {
    ElMessage.info('学期已设置')
    return
  }

  try {
    await activateDatabase(formData.semester)
    originalSemester.value = formData.semester
    isDatabaseActivated.value = true
    courses.value = []
    ElMessage.success('学期设置成功，数据库已激活')
  } catch (error) {
    console.error('设置学期失败:', error)
    ElMessage.error('设置学期失败。请确保已将培养方案放置在config目录下，并命名为plan.pdf')
  }
}

// 加载配置
const loadConfig = async () => {
  try {
    const config = await getConfig()
    
    // 更新表单数据
    formData.apiProvider = config.model.base_url
    formData.modelName = config.model.model_name
    formData.apiKey = config.model.api_key
    formData.temperature = config.model.temperature
    formData.topP = config.model.top_p
    formData.stream = config.model.stream
    
    formData.studentId = config.user.student_id
    formData.password = config.user.portal_password
    formData.grade = config.user.grade
    formData.semester = config.user.semester
    formData.userDescription = config.user.introduction
    formData.chrome_user_data_dir = config.crawler.chrome_user_data_dir

    // 新增配置项
    formData.num_timetable = config.course.num_timetable
    formData.num_search = config.crawler.num_search
    formData.sleep_after_search = config.crawler.sleep_after_search
    formData.sleep_between_scroll = config.crawler.sleep_between_scroll
    formData.sleep_random_range = config.crawler.sleep_random_range

    // 保存原始学期
    originalSemester.value = formData.semester

    // 激活数据库
    if (formData.semester) {
      await activateDatabase(formData.semester)
      isDatabaseActivated.value = true
      courses.value = await fetchCourseRawInfo(config.course.course_list)
    } else {
      courses.value = [];
      isDatabaseActivated.value = false
    }
    
    // 更新学分和偏好
    minCredits.value = config.course.min_credit
    maxCredits.value = config.course.max_credit
    coursePreference.value = config.course.preference
    
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

// 删除所有课程
const deleteAllCourses = () => {
  ElMessageBox.confirm(
    '确定要删除所有课程吗？此操作不可恢复。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    courses.value = []
    ElMessage.success('已删除所有课程')
  }).catch(() => {
    // 用户取消删除，不做任何操作
  })
}

onMounted(async () => {
  await loadConfig()
})
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
          <el-col :span="24">
            <el-divider content-position="left">用户配置</el-divider>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="年级">
              <el-input v-model="formData.grade" placeholder="请输入年级（如大一）" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="当前学期">
              <el-input v-model="formData.semester" placeholder="请输入当前学期（如2024-2025-2）" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <el-button type="primary" @click="handleSetSemester">设定学期</el-button>
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
            <el-divider content-position="left">大模型配置</el-divider>
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
            <el-form-item label="模型温度">
              <el-slider
                v-model="formData.temperature"
                :min="0"
                :max="1.5"
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
        <el-row :gutter="20">
          <el-col :span="24">
            <el-divider content-position="left">爬虫配置</el-divider>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="搜索评测数" label-width="100px">
              <el-input-number 
                v-model="formData.num_search" 
                :min="1" 
                :max="20"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="搜索后等待" label-width="100px">
              <el-input-number 
                v-model="formData.sleep_after_search" 
                :min="1" 
                :max="30"
                :step="1"
              />
              <span class="unit-label">秒</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="滚动等待" label-width="100px">
              <el-input-number 
                v-model="formData.sleep_between_scroll" 
                :min="0.1" 
                :max="2"
                :step="0.1"
              />
              <span class="unit-label">秒</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="随机比例" label-width="100px">
              <el-input-number 
                v-model="formData.sleep_random_range" 
                :min="0" 
                :max="1"
                :step="0.1"
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
            <el-button type="danger" @click="deleteAllCourses">删除所有课程</el-button>
            <el-button type="success" @click="handleFileImport">导入培养方案</el-button>
            <el-button type="primary" @click="showAddCourseDialog">手动添加课程</el-button>
          </div>
        </div>
      </template>
      <el-collapse v-model="activeNames" class="course-collapse">
        <el-collapse-item v-for="(course, courseIndex) in courses" :key="courseIndex" :name="courseIndex">
          <template #title>
            <div class="collapse-title">
              <span class="course-list-name">{{ course.name }}</span>
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
          <el-form-item label="生成课表数">
            <el-input-number 
              v-model="formData.num_timetable" 
              :min="1" 
              :max="10"
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
      <el-button type="success" size="large" @click="() => savePreference(formData, courses, minCredits, maxCredits, coursePreference)">保存</el-button>
      <el-button type="primary" size="large" @click="handleCourseEvaluation">开始搜索推荐</el-button>
    </div>

    <!-- 课程评价展示区域 -->
    <el-card v-if="Object.keys(courseEvaluationStatus).length > 0" class="evaluation-card">
      <template #header>
        <div class="card-header">
          <span>课程评价</span>
        </div>
      </template>
      <el-tabs v-model="activeEvaluationTab" type="card">
        <el-tab-pane 
          v-for="course in courses" 
          :key="course.name" 
          :label="course.name" 
          :name="course.name"
        >
          <div class="evaluation-content">
            <div class="status-badge" :class="courseEvaluationStatus[course.name].toLowerCase()">
              {{ courseEvaluationStatus[course.name] }}
            </div>
            <div class="evaluation-text" v-if="courseEvaluationContent[course.name]">
              {{ courseEvaluationContent[course.name] }}
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 添加课程对话框 -->
    <el-dialog v-model="addCourseDialogVisible" title="添加课程" width="500px">
      <el-form :model="newCourse" label-width="100px">
        <el-form-item label="课程名称" required>
          <el-input v-model="newCourse.name" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="教师名称">
          <el-input v-model="newCourse.teacher" placeholder="请输入教师名称（选填）" />
        </el-form-item>
        <el-form-item label="班级编号">
          <el-input v-model="newCourse.class_id" placeholder="请输入班级编号（选填）" />
        </el-form-item>
        <el-form-item>
          <el-alert
            title="选填为筛选条件，将添加所有符合条件的班级"
            type="info"
            :closable="false"
            show-icon
          />
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

    <!-- 添加班级对话框 -->
    <el-dialog v-model="addClassDialogVisible" title="添加班级" width="500px">
      <el-form :model="newClass" label-width="100px">
        <el-form-item label="课程名称">
          <el-input :value="addingCourseName" disabled />
        </el-form-item>
        <el-form-item label="班级编号">
          <el-input v-model="newClass.class_id" placeholder="请输入班级编号（选填）" />
        </el-form-item>
        <el-form-item label="教师名称">
          <el-input v-model="newClass.teacher" placeholder="请输入教师名称（选填）" />
        </el-form-item>
        <el-form-item>
          <el-alert
            title="以上为筛选条件，将添加所有符合条件的班级"
            type="info"
            :closable="false"
            show-icon
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addClassDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAddClass">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 课表展示区域 -->
    <el-card v-if="timetables.length > 0" class="timetable-card">
      <template #header>
        <div class="card-header">
          <span>课表方案</span>
          <div class="timetable-tabs">
            <el-radio-group v-model="activeTimetableIndex">
              <el-radio-button 
                v-for="(_, index) in timetables" 
                :key="index" 
                :label="index"
              >
                方案 {{ index + 1 }}
              </el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>
      
      <el-table
        :data="generateTableData(timetables[activeTimetableIndex])"
        border
        style="width: 100%"
        :span-method="({ row, column, rowIndex, columnIndex }) => {
          if (columnIndex === 0) { // the first column (节次)
            return { rowspan: 1, colspan: 1 }
          }
          const cell = row[column.property]
          if (cell) {
            if(cell.merged) {
              return { rowspan: 0, colspan: 0 }
            }
            return { rowspan: cell.rowspan, colspan: cell.colspan }
          }
          return { rowspan: 1, colspan: 1 }
        }"
      >
        <el-table-column
          prop="time"
          label="节次"
          width="80"
          fixed
        />
        <el-table-column
          prop="周一"
          label="周一"
        >
          <template #default="scope">
            <div v-if="scope.row['周一']" class="course-cell" :style="scope.row['周一'].bgColor ? { backgroundColor: scope.row['周一'].bgColor } : {}">
              <div class="course-name">{{ scope.row['周一'].name }}</div>
              <div class="course-teacher">{{ scope.row['周一'].teacher }}</div>
              <div class="course-location">{{ scope.row['周一'].location }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="周二"
          label="周二"
        >
          <template #default="scope">
            <div v-if="scope.row['周二']" class="course-cell" :style="scope.row['周二'].bgColor ? { backgroundColor: scope.row['周二'].bgColor } : {}">
              <div class="course-name">{{ scope.row['周二'].name }}</div>
              <div class="course-teacher">{{ scope.row['周二'].teacher }}</div>
              <div class="course-location">{{ scope.row['周二'].location }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="周三"
          label="周三"
        >
          <template #default="scope">
            <div v-if="scope.row['周三']" class="course-cell" :style="scope.row['周三'].bgColor ? { backgroundColor: scope.row['周三'].bgColor } : {}">
              <div class="course-name">{{ scope.row['周三'].name }}</div>
              <div class="course-teacher">{{ scope.row['周三'].teacher }}</div>
              <div class="course-location">{{ scope.row['周三'].location }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="周四"
          label="周四"
        >
          <template #default="scope">
            <div v-if="scope.row['周四']" class="course-cell" :style="scope.row['周四'].bgColor ? { backgroundColor: scope.row['周四'].bgColor } : {}">
              <div class="course-name">{{ scope.row['周四'].name }}</div>
              <div class="course-teacher">{{ scope.row['周四'].teacher }}</div>
              <div class="course-location">{{ scope.row['周四'].location }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="周五"
          label="周五"
        >
          <template #default="scope">
            <div v-if="scope.row['周五']" class="course-cell" :style="scope.row['周五'].bgColor ? { backgroundColor: scope.row['周五'].bgColor } : {}">
              <div class="course-name">{{ scope.row['周五'].name }}</div>
              <div class="course-teacher">{{ scope.row['周五'].teacher }}</div>
              <div class="course-location">{{ scope.row['周五'].location }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="周六"
          label="周六"
        >
          <template #default="scope">
            <div v-if="scope.row['周六']" class="course-cell" :style="scope.row['周六'].bgColor ? { backgroundColor: scope.row['周六'].bgColor } : {}">
              <div class="course-name">{{ scope.row['周六'].name }}</div>
              <div class="course-teacher">{{ scope.row['周六'].teacher }}</div>
              <div class="course-location">{{ scope.row['周六'].location }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          prop="周日"
          label="周日"
        >
          <template #default="scope">
            <div v-if="scope.row['周日']" class="course-cell" :style="scope.row['周日'].bgColor ? { backgroundColor: scope.row['周日'].bgColor } : {}">
              <div class="course-name">{{ scope.row['周日'].name }}</div>
              <div class="course-teacher">{{ scope.row['周日'].teacher }}</div>
              <div class="course-location">{{ scope.row['周日'].location }}</div>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<!-- 引入全局样式文件 -->
<style src="@/styles/course.css"></style>
<style src="@/styles/app.css"></style>
<style src="@/styles/element-plus-overrides.css"></style>
<style src="@/styles/evaluation.css"></style>