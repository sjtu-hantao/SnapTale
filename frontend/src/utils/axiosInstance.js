// api.js
import axios from 'axios';

// 创建Axios实例
const apiClient = axios.create({
  baseURL: window.backend_url, // 替换为你的API基础URL
  headers: {
    'Content-Type': 'application/json',
    // 其他默认请求头
  },
  // 其他Axios配置
});

// 添加请求拦截器
// apiClient.interceptors.request.use(
//   (config) => {
//     // 在请求发送之前做一些处理
//     // 例如添加认证token
//     const token = localStorage.getItem('token');
//     if (token) {
//       config.headers.Authorization = `Bearer ${token}`;
//     }
//     return config;
//   },
//   (error) => {
//     return Promise.reject(error);
//   }
// );

// 添加响应拦截器
// apiClient.interceptors.response.use(
//   (response) => {
//     // 对响应数据做一些处理
//     return response;
//   },
//   (error) => {
//     // 对响应错误做一些处理
//     if (error.response && error.response.status === 401) {
//       // 处理未授权错误，例如重定向到登录页面
//     }
//     return Promise.reject(error);
//   }
// );

export default apiClient;
