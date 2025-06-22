import axios from 'axios'
import { BASE_URL } from '@/utils'
import { formatCourseInfoToClass } from '@/utils/courseFormatter'

/**
 * 获取所有满足筛选条件的课程信息
 * @param {string} course_name - 课程名称
 * @param {number|null} [class_id=null] - 课程编号，可选
 * @param {string|null} [teacher=null] - 教师姓名，可选
 * @returns {Promise<Array>} 返回课程信息数组
 */
export const fetchCourse = async (course_name, class_id = null, teacher = null, accept_advance = true, fuzzy_match = true) => {
    try {
        const response = await axios.post(`${BASE_URL}/course/info`, {
            name: course_name,
            class_id: class_id,
            teacher: teacher,
            fuzzy_matching: fuzzy_match,
            accept_advanced_class: accept_advance
        })
        return response.data
    } catch (error) {
        console.error('获取课程信息失败:', error)
        throw error
    }
}

/**
 * 批量获取课程信息，格式为config.json中的course.course_list的格式
 * @param {Array<{name: string, class_ids: Array<number>}>} courses_raw - 课程列表
 * @returns {Promise<Array>} 返回处理后的课程信息数组
 */
export const fetchCourseRawInfo = async (courses_raw) => {
    try {
        // 创建一个数组来存储所有课程的请求
        const courseRequests = courses_raw.flatMap(course => 
            course.class_ids.map(classId => ({
                name: course.name,
                class_id: classId
            }))
        )

        // 使用Promise.all并行处理所有请求
        const responses = await Promise.all(
            courseRequests.map(request => fetchCourse(request.name, request.class_id, null, false, false))
        )
        
        // responses : List[List[Course]], 需要转换为List[Course]
        return courseDataToMapArray(responses.flat())

    } catch (error) {
        console.error('批量获取课程信息失败:', error)
        throw error
    }
}

export const fetchCourseByPlan = async (semester, grade, plan_path) => {
    try {
        const response = await axios.post(`${BASE_URL}/course/plan`, {
            semester: semester,
            grade: grade,
            plan_path: plan_path
        })
        return response.data
    } catch (error) {
        console.error('获取课程信息失败:', error)
        throw error
    }
}

export const courseDataToMapArray = (courseData) => {
    const courseMap = new Map()
    
    courseData.forEach(course => {
        if(!course || course.name === "Not found") {
            return
        }

        if (!courseMap.has(course.name)) {
            courseMap.set(course.name, {
                name: course.name,
                classes: []
            })
        }        courseMap.get(course.name).classes.push(formatCourseInfoToClass(course))
    })

    return Array.from(courseMap.values())
}

/**
 * 激活数据库
 * @param {string} semester - 学期，格式如 "2024-2025-2"
 * @returns {Promise<void>}
 */
export const activateDatabase = async (semester) => {
    try {
        await axios.post(`${BASE_URL}/course/activate?semester=${semester}`)
    } catch (error) {
        console.error('激活数据库失败:', error)
        throw error
    }
}

// 获取课程评价
export const getCourseEvaluation = async (courseName, rawText, choices, modelConfig, onChunk) => {
  try {
    const response = await fetch(`${BASE_URL}/llm/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        course_name: courseName,
        raw_text: rawText,
        choices: choices,
        model: modelConfig,
        model_name: modelConfig.name // 兼容性
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      if (chunk && onChunk) {
        onChunk(chunk);
      }
    }
  } catch (error) {
    console.error('获取课程评价失败:', error);
    throw error;
  }
};

export const readPlanPDF = async () => {
    try {
        const response = await axios.post(`${BASE_URL}/course/plan_pdf`)
        return response.data
    } catch (error) {
        console.error('读取培养方案失败:', error)
        throw error
    }
}

export const genPlan = async (requestData) => {
    try {
        const response = await axios.post(`${BASE_URL}/llm/plan`, requestData)
        return response.data
    } catch (error) {
        console.error('生成选课方案失败:', error)
        throw error
    }
}

export const hasPlan = async() => {
    try {
        const response = await axios.get(`${BASE_URL}/course/has_plan_pdf`)
        return response.data
    } catch (error) {
        console.error('检查是否有选课方案失败:', error)
        throw error
    }
}

/**
 * 流式生成课表，支持实时显示推理过程
 * @param {Object} requestData - 请求数据
 * @param {Function} onReasoningChunk - 推理过程回调函数
 * @param {Function} onResult - 结果回调函数
 * @param {Object} modelConfig - 模型配置对象
 * @returns {Promise<void>}
 */
export const genPlanStream = async (requestData, onReasoningChunk, onResult, modelConfig) => {

    console.log('开始流式生成选课方案:', requestData, '模型配置:', modelConfig)

    try {
        // 添加模型配置到请求数据中
        const requestWithModel = {
            ...requestData,
            model: modelConfig,
            model_name: modelConfig.name // 兼容性
        }
        
        const response = await fetch(`${BASE_URL}/llm/plan_stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestWithModel)
        })

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()

        while (true) {
            const { done, value } = await reader.read()
            if (done) break

            const chunk = decoder.decode(value, { stream: true })
            const lines = chunk.split('\n').filter(line => line.trim())

            for (const line of lines) {
                try {
                    const data = JSON.parse(line)
                    if (data.type === 'reasoning') {
                        onReasoningChunk && onReasoningChunk(data)
                    } else if (data.type === 'result') {
                        onResult && onResult(data.data)
                    }
                } catch (e) {
                    console.warn('解析JSON失败:', e, '原始数据:', line)
                }
            }
        }
    } catch (error) {
        console.error('流式生成选课方案失败:', error)
        throw error
    }
}

/**
 * 上传培养方案PDF文件
 * @param {File} file - 要上传的PDF文件
 * @returns {Promise<Object>} 上传结果
 */
export const uploadPlanPdf = async (file) => {
  try {
    // 创建FormData对象
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post(
      `${BASE_URL}/course/upload_plan_pdf`, 
      formData, 
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('上传培养方案PDF失败:', error);
    throw error;
  }
};