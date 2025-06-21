/**
 * 课程数据格式化工具函数
 */

/**
 * 安全地解析课程ID，如果无法解析则返回null
 * @param {string|number} classId - 课程ID字符串或数字
 * @returns {number|null} 解析后的数字ID或null
 */
export const parseClassId = (classId) => {
  if (!classId) return null
  
  const parsed = parseInt(classId)
  return isNaN(parsed) ? null : parsed
}

/**
 * 将API返回的课程信息转换为前端所需的班级对象格式
 * @param {Object} courseInfo - API返回的课程信息对象
 * @returns {Object} 前端所需的班级对象格式
 */
export const formatCourseInfoToClass = (courseInfo) => {
  return {
    id: courseInfo.class_id.toString(),
    teacher: courseInfo.teacher,
    time: courseInfo.time,
    location: courseInfo.location,
    course_id: courseInfo.course_id,
    note: courseInfo.note,
    credit: courseInfo.credit
  }
}

/**
 * 批量转换课程信息数组为班级对象数组
 * @param {Array} courseInfoArray - API返回的课程信息数组
 * @returns {Array} 前端所需的班级对象数组
 */
export const formatCourseInfoArrayToClasses = (courseInfoArray) => {
  return courseInfoArray.map(formatCourseInfoToClass)
}
