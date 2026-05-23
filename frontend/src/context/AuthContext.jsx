import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { login as apiLogin, register as apiRegister, getMe } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

  // Re-hydrate user from stored token on mount
  useEffect(() => {
    const token = localStorage.getItem('access')
    if (!token) { setLoading(false); return }
    getMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
      })
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async credentials => {
    const data = await apiLogin(credentials)
    localStorage.setItem('access',  data.access)
    localStorage.setItem('refresh', data.refresh)
    setUser(data.user)
    return data
  }, [])

  const register = useCallback(async payload => {
    return apiRegister(payload)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
