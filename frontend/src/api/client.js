import axios from 'axios'

const client = axios.create({ baseURL: '/api' })

// Attach access token to every request
client.interceptors.request.use(config => {
  const token = localStorage.getItem('access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// On 401: try to refresh, then retry original request
let refreshing = false
let queue = []

const processQueue = (err, token) =>
  queue.splice(0).forEach(p => (err ? p.reject(err) : p.resolve(token)))

client.interceptors.response.use(
  res => res,
  async err => {
    const orig = err.config
    if (err.response?.status !== 401 || orig._retry) return Promise.reject(err)

    if (refreshing) {
      return new Promise((resolve, reject) => queue.push({ resolve, reject }))
        .then(token => { orig.headers.Authorization = `Bearer ${token}`; return client(orig) })
    }

    orig._retry = true
    refreshing = true

    const refresh = localStorage.getItem('refresh')
    if (!refresh) { window.location.href = '/login'; return Promise.reject(err) }

    try {
      const { data } = await axios.post('/api/auth/token/refresh/', { refresh })
      localStorage.setItem('access', data.access)
      client.defaults.headers.common.Authorization = `Bearer ${data.access}`
      processQueue(null, data.access)
      orig.headers.Authorization = `Bearer ${data.access}`
      return client(orig)
    } catch (e) {
      processQueue(e, null)
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      window.location.href = '/login'
      return Promise.reject(e)
    } finally {
      refreshing = false
    }
  }
)

export default client
