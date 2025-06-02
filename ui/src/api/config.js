import axios from 'axios'
import { BASE_URL } from '@/utils'

/**
 * 获取配置文件内容
 * @returns {Promise<Object>} 配置信息
 */
export const getConfig = async () => {
    console.log('获取配置文件内容...')
    try {
        const response = await axios.get(`${BASE_URL}/config`)
        return response.data
    } catch (error) {
        console.error('获取配置失败:', error)
        throw error
    }
}

/**
 * 保存配置文件内容
 * @param {Object} config - 配置信息
 * @returns {Promise<Object>} 保存结果
 */
export const saveConfig = async (config) => {
    try {
        const response = await axios.post(`${BASE_URL}/config`, config)
        return response.data
    } catch (error) {
        console.error('保存配置失败:', error)
        throw error
    }
} 