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

  // 解析课程时间字符串，返回 [{ dayIdx, start, end }]
  function parseCourseTime(timeStr) {
    if (!timeStr) return []
    const result = []
    const segments = timeStr.split(';').map(seg => seg.trim()).filter(Boolean)
    segments.forEach(segment => {
      // 例：all,1,3-4
      const parts = segment.split(',')
      if (parts.length < 3) return
      const dayIdx = parseInt(parts[1], 10) - 1 // 0=周一
      const [start, end] = parts[2].split('-').map(x => parseInt(x, 10))
      if (isNaN(dayIdx) || isNaN(start) || isNaN(end)) return
      result.push({ dayIdx, start, end })
    })
    return result
  }

  // 预设一组颜色，循环分配
  const colorPalette = [
    '#FFEBEE', '#E3F2FD', '#E8F5E9', '#FFFDE7', '#F3E5F5', '#FBE9E7', '#E0F2F1', '#FFF3E0', '#F9FBE7', '#ECEFF1',
    '#FFCDD2', '#BBDEFB', '#C8E6C9', '#FFF9C4', '#D1C4E9', '#FFCCBC', '#B2DFDB', '#FFE0B2', '#F0F4C3', '#CFD8DC'
  ]
  const courseColorMap = new Map()
  let colorIdx = 0

  // 为每门课分配颜色
  timetable.forEach(course => {
    if (!courseColorMap.has(course.name)) {
      courseColorMap.set(course.name, colorPalette[colorIdx % colorPalette.length])
      colorIdx++
    }
  })

  // 解析课程时间并填入表格
  timetable.forEach((course) => {
    const timeSlots = parseCourseTime(course.time)
    const bgColor = courseColorMap.get(course.name)
    timeSlots.forEach(({ dayIdx, start, end }) => {
      for (let period = start; period <= end; period++) {
        const rowIdx = period - 1
        if (rowIdx >= 0 && rowIdx < tableData.length && dayIdx >= 0 && dayIdx < days.length) {
          if (period === start) {
            tableData[rowIdx][days[dayIdx]] = {
              ...course,
              colspan: 1,
              rowspan: end - start + 1,
              merged: false,
              bgColor
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