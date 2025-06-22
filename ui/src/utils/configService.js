import { ElMessage } from 'element-plus'
import { saveConfig } from '@/api/config'
import { unref } from 'vue'

export const savePreference = async (formData, courses, minCredits, maxCredits, coursePreference) => {
  try {    const config = {
      model: {
        base_url: formData.apiProvider,
        model_name: formData.modelName, // 保留旧字段以兼容
        evaluate_model: {
          name: formData.evaluateModelName,
          temperature: formData.evaluateModelTemperature,
          top_p: formData.evaluateModelTopP
        },
        gen_plan_model: {
          name: formData.genPlanModelName,
          temperature: formData.genPlanModelTemperature,
          top_p: formData.genPlanModelTopP
        },
        api_key: formData.apiKey,
        temperature: formData.temperature, // 兼容性
        top_p: formData.topP, // 兼容性
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
          class_ids: [...new Set(course.classes.map(c => parseInt(c.id)))] // 使用Set去重，防止重复班号
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