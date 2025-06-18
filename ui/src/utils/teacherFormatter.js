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
