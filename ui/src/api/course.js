import axios from 'axios'
import { BASE_URL } from '@/config'

/**
 * 获取所有满足筛选条件的课程信息
 * @param {string} course_name - 课程名称
 * @param {number|null} [class_id=null] - 课程编号，可选
 * @param {string|null} [teacher=null] - 教师姓名，可选
 * @returns {Promise<Array>} 返回课程信息数组
 */
export const fetchCourse = async (course_name, class_id = null, teacher = null) => {
    try {
        const response = await axios.post(`${BASE_URL}/course/info`, {
            name: course_name,
            class_id: class_id,
            teacher: teacher
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
            courseRequests.map(request => fetchCourse(request.name, request.class_id))
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
        }
        courseMap.get(course.name).classes.push({
            id: course.class_id.toString(),
            teacher: course.teacher,
            time: course.time,
            location: course.location,
            course_id: course.course_id,
            note: course.note,
            credit: course.credit
        })
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
export const getCourseEvaluation = async (courseName, rawText, onChunk) => {
  try {
    const response = await fetch(`${BASE_URL}/llm/evaluate_test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        course_name: courseName,
        raw_text: rawText
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