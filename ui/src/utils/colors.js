// 课程颜色配置
export const colorPalette = [
  '#FFEBEE', '#E3F2FD', '#E8F5E9', '#FFFDE7', '#F3E5F5', '#FBE9E7', '#E0F2F1', '#FFF3E0', '#F9FBE7', '#ECEFF1',
  '#FFCDD2', '#BBDEFB', '#C8E6C9', '#FFF9C4', '#D1C4E9', '#FFCCBC', '#B2DFDB', '#FFE0B2', '#F0F4C3', '#CFD8DC'
]

// 为课程分配颜色的函数
export const createCourseColorMap = (timetable) => {
  const courseColorMap = new Map()
  let colorIdx = 0

  // 为每门课分配颜色
  timetable.forEach(course => {
    if (!courseColorMap.has(course.name)) {
      courseColorMap.set(course.name, colorPalette[colorIdx % colorPalette.length])
      colorIdx++
    }
  })

  return courseColorMap
}
