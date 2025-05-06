import axios from 'axios'
import { BASE_URL } from '@/config'

/**
 * 获取单个课程信息
 * @param {string} course_name - 课程名称
 * @param {number|null} [class_id=null] - 课程编号，可选
 * @param {string|null} [teacher=null] - 教师姓名，可选
 * @returns {Promise<Array>} 返回课程信息数组
 */
export const fetchSingleCourse = async (course_name, class_id = null, teacher = null) => {
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
 * 获取所有课程信息
 * @param {string} course_name - 课程名称
 * @returns {Promise<Array>} 返回课程信息数组
 */
export const fetchAllCourseOfName = async (course_name) => {
    try {
        const response = await axios.post(`${BASE_URL}/course/info`, {
            name: course_name
        })
        return response.data
    } catch (error) {
        console.error('获取课程信息失败:', error)
        throw error
    }
}

/**
 * 批量获取课程信息
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
            courseRequests.map(request => fetchSingleCourse(request.name, request.class_id))
        )

        // 将API返回的数据转换为前端需要的格式
        const courseMap = new Map()
        
        responses.forEach(response => {
            // response是一个数组，我们需要取第一个元素
            const courseData = response[0]
            if (!courseData || courseData.name === "Not found") {
                return
            }
            
            if (!courseMap.has(courseData.name)) {
                courseMap.set(courseData.name, {
                    name: courseData.name,
                    classes: []
                })
            }
            
            courseMap.get(courseData.name).classes.push({
                id: courseData.class_id,
                teacher: courseData.teacher,
                time: courseData.time,
                location: courseData.location
            })
        })

        // 将Map转换为数组
        return Array.from(courseMap.values())
    } catch (error) {
        console.error('批量获取课程信息失败:', error)
        throw error
    }
}