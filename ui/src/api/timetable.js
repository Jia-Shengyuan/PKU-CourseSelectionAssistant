

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

  // 为每个课程分配时间
  timetable.forEach((course, index) => {
    // 计算课程位置：每门课占两节，按顺序排列。第一节课为周一1-2，第二节课为周二3-4，以此类推
    const dayIndex = index % 7
    const periodIndex = index * 2
    
    if (periodIndex < 12) {  // 确保不超过12节课
      // 填入课程信息
      tableData[periodIndex][days[dayIndex]] = {
        ...course,
        colspan: 1,
        rowspan: 2,
        merged: false
      }
      // 下一行设为null，表示被合并
      tableData[periodIndex + 1][days[dayIndex]] = {
        text: '',
        colspan: 0,
        rowspan: 0,
        merged: true
      }
    }
  })

  return tableData
}