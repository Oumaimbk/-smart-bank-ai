import client from './client'

export const login    = credentials => client.post('/auth/login/', credentials).then(r => r.data)
export const register = payload     => client.post('/auth/register/', payload).then(r => r.data)
export const getMe    = ()          => client.get('/auth/me/').then(r => r.data)
