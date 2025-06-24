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

/**
 * 将后端配置映射到前端表单数据
 * @param {Object} config - 后端配置对象
 * @param {Object} formData - 前端表单数据对象
 */
export const mapConfigToFormData = (config, formData) => {
  // 模型配置
  formData.apiProvider = config.model.base_url
  formData.modelName = config.model.model_name // 保留旧的以兼容
  formData.evaluateModelName = config.model.evaluate_model?.name || config.model.model_name
  formData.evaluateModelTemperature = config.model.evaluate_model?.temperature || 0.75
  formData.evaluateModelTopP = config.model.evaluate_model?.top_p || 0.9
  formData.genPlanModelName = config.model.gen_plan_model?.name || config.model.model_name
  formData.genPlanModelTemperature = config.model.gen_plan_model?.temperature || 0.7
  formData.genPlanModelTopP = config.model.gen_plan_model?.top_p || 0.95
  formData.apiKey = config.model.api_key
  formData.temperature = config.model.temperature || formData.evaluateModelTemperature // 兼容性
  formData.topP = config.model.top_p || formData.evaluateModelTopP // 兼容性
  formData.stream = config.model.stream
  
  // 用户配置
  formData.studentId = config.user.student_id
  formData.password = config.user.portal_password
  formData.grade = config.user.grade
  formData.semester = config.user.semester
  formData.userDescription = config.user.introduction
  formData.chrome_user_data_dir = config.crawler.chrome_user_data_dir

  // 课程配置
  formData.num_timetable = config.course.num_timetable
  
  // 爬虫配置
  formData.num_search = config.crawler.num_search
  formData.sleep_after_search = config.crawler.sleep_after_search
  formData.sleep_between_scroll = config.crawler.sleep_between_scroll
  formData.sleep_random_range = config.crawler.sleep_random_range
}