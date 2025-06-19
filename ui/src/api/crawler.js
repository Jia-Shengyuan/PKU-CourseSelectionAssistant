import axios from 'axios'
import { BASE_URL } from '@/utils'

// 登录树洞
export const loginTreehole = async () => {
  try {
    await axios.post(`${BASE_URL}/crawler/login`)
  } catch (error) {
    console.error('登录树洞失败:', error)
    throw error
  }
}

// 搜索课程评价
export const searchTreehole = async (courseName, num_search = 3, teacherCodes = []) => {
    try {
      const response = await axios.post(`${BASE_URL}/crawler/search_courses`, {
        course_name: courseName,
        max_len: num_search,  // 可以根据需要调整
        teachers: teacherCodes // 添加教师代码列表参数
      });
      return response.data;
    } catch (error) {
      console.error('搜索树洞失败:', error);
      throw error;
    }
  };

export const closeTreehole = async () => {
  try {
    await axios.post(`${BASE_URL}/crawler/close`)
  } catch (error) {
    console.error('关闭树洞网页失败:', error)
    throw error
  }
}