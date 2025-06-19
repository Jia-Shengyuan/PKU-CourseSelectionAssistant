// 格式化教师姓名，移除拼音缩写部分
export const formatTeacherName = (teacherName) => {
  if (!teacherName) return ''
  return teacherName.split(',').map(name => {
    const trimmedName = name.trim()
    // 查找 '/' 字符的位置
    const slashIndex = trimmedName.indexOf('/')
    if (slashIndex !== -1) {
      // 找到 '/' 后，移除 '/' 及其后面的连续英文字母
      const beforeSlash = trimmedName.substring(0, slashIndex)
      const afterSlash = trimmedName.substring(slashIndex + 1)
      // 移除连续的英文字母，保留其他字符（如括号和中文）
      const cleanedAfterSlash = afterSlash.replace(/^[a-zA-Z]+/, '')
      return beforeSlash + cleanedAfterSlash
    }
    return trimmedName
  }).join('，')
}

export const extractTeacherCodes = (input) => {

  if (input && typeof input === 'object' && input.classes && Array.isArray(input.classes)) {
    const allCodes = []
    input.classes.forEach(cls => {
      if (cls.teacher) {
        const codes = extractTeacherCodesFromString(cls.teacher)
        allCodes.push(...codes)
      }
    })
    
    return [...new Set(allCodes)]
  } 
  
  // 如果输入是字符串，直接提取缩写
  if (typeof input === 'string') {
    return extractTeacherCodesFromString(input)
  }
  
  // 其他情况返回空数组
  return []
}

// 从教师名称字符串中提取所有教师的缩写代码
const extractTeacherCodesFromString = (teacherName) => {

  if (!teacherName) return []
  
  const teacherCodes = []
  
  // 使用正则表达式匹配所有 "/" 后面跟着的连续英文字母
  const regex = /\/([a-zA-Z]+)/g
  let match
  
  // 循环查找所有匹配项
  while ((match = regex.exec(teacherName)) !== null) {
    if (match[1]) {
      teacherCodes.push(match[1])
    }
  }
  
  // 返回提取的所有代码（不在这里去重，等所有班级处理完后再去重）
  return teacherCodes
}
