import { ElMessage } from 'element-plus'
import { saveConfig } from '@/api/config'
import { unref } from 'vue'

export const savePreference = async (formData, courses, minCredits, maxCredits, coursePreference) => {
  try {
    const config = {
      model: {
        base_url: formData.apiProvider,
        model_name: formData.modelName,
        api_key: formData.apiKey,
        temperature: formData.temperature,
        top_p: formData.topP,
        stream: formData.stream
      },
      user: {
        student_id: formData.studentId,
        portal_password: formData.password,
        grade: formData.grade,
        semester: formData.semester,
        introduction: formData.userDescription
      },
      course: {
        course_list: unref(courses).map(course => ({
          name: course.name,
          class_ids: course.classes.map(c => parseInt(c.id))
        })),
        min_credit: unref(minCredits),
        max_credit: unref(maxCredits),
        preference: unref(coursePreference),
        num_timetable: formData.num_timetable
      },
      crawler: {
        chrome_user_data_dir: formData.chrome_user_data_dir,
        num_search: formData.num_search,
        sleep_after_search: formData.sleep_after_search,
        sleep_between_scroll: formData.sleep_between_scroll,
        sleep_random_range: formData.sleep_random_range
      }
    }
    
    await saveConfig(config)
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存失败')
  }
}