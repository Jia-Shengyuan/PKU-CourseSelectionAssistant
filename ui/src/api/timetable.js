

export const generateTableData = (timetable) => {

    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    const periods = Array.from({ length: 12 }, (_, i) => i + 1)
    
    return periods.map(period => {
      const row = { time: `第${period}节` }
      days.forEach((day, dayIndex) => {
        // 每两节课为一组
        const courseIndex = Math.floor(period / 2)
        if (period % 2 === 1 && timetable[courseIndex]) {
          row[day] = timetable[courseIndex]
        }
      })
      return row
    })
    
  }