import { createCourseColorMap } from '@/utils/colors'

/**
 * 计算指定课表的总学分
 * @param {Array} timetable - 课表数组
 * @returns {number} 总学分
 */
export const calculateTimetableCredits = (timetable) => {
  if (!timetable || !Array.isArray(timetable) || timetable.length === 0) {
    return 0
  }
  let total = 0
  timetable.forEach(course => {
    if (course.credit) {
      total += Number(course.credit)
    }
  })
  return total
}

export const generateTableData = (timetable) => {
  
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const periods = Array.from({ length: 12 }, (_, i) => i + 1)
  
  // 初始化表格数据
  const tableData = periods.map(period => {
    const row = { time: `第${period}节` }
    days.forEach(day => {
      row[day] = null
    })
    return row
  })

  if (!timetable || timetable.length === 0) {
    return tableData
  }
  // 解析课程时间字符串，返回 [{ dayIdx, start, end, weekType }]
  function parseCourseTime(timeStr) {
    if (!timeStr) return []
    const result = []
    const segments = timeStr.split(';').map(seg => seg.trim()).filter(Boolean)
    segments.forEach(segment => {
      // 例：all,1,3-4 或 odd,1,3-4 或 even,1,3-4
      const parts = segment.split(',')
      if (parts.length < 3) return
      const weekType = parts[0] // all, odd, even
      const dayIdx = parseInt(parts[1], 10) - 1 // 0=周一
      const [start, end] = parts[2].split('-').map(x => parseInt(x, 10))
      if (isNaN(dayIdx) || isNaN(start) || isNaN(end)) return
      result.push({ dayIdx, start, end, weekType })
    })
    return result
  }

  // 将weekType转换为中文显示
  function getWeekTypeText(weekType) {
    switch (weekType) {
      case 'all': return '每周'
      case 'odd': return '单周'
      case 'even': return '双周'
      default: return '每周'
    }
  }
  // 预设一组颜色，循环分配
  const courseColorMap = createCourseColorMap(timetable)
  // 解析课程时间并填入表格
  timetable.forEach((course) => {
    const timeSlots = parseCourseTime(course.time)
    const bgColor = courseColorMap.get(course.name)
    timeSlots.forEach(({ dayIdx, start, end, weekType }) => {
      for (let period = start; period <= end; period++) {
        const rowIdx = period - 1
        if (rowIdx >= 0 && rowIdx < tableData.length && dayIdx >= 0 && dayIdx < days.length) {
          if (period === start) {
            tableData[rowIdx][days[dayIdx]] = {
              ...course,
              colspan: 1,
              rowspan: end - start + 1,
              merged: false,
              bgColor,
              weekType: getWeekTypeText(weekType)
            }
          } else {
            tableData[rowIdx][days[dayIdx]] = {
              text: '',
              colspan: 0,
              rowspan: 0,
              merged: true,
              bgColor
            }
          }
        }
      }
    })
  })
  return tableData
}
