import axios from 'axios'
import { BASE_URL } from '@/config'

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
export const searchTreehole = async (courseName) => {
    try {
      const response = await axios.post(`${BASE_URL}/crawler/search_courses`, {
        course_name: courseName,
        max_len: 3  // 可以根据需要调整
      });
      return response.data;
    } catch (error) {
      console.error('搜索树洞失败:', error);
      throw error;
    }
  };