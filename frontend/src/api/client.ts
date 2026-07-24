import axios from 'axios'
import { toast } from 'sonner'

const client = axios.create({
  baseURL: '/api',
})

client.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      toast.error('Sesión expirada. Inicia sesión nuevamente.')
    }
    const message = error.response?.data?.detail ?? error.message
    return Promise.reject(new Error(message))
  }
)

export default client