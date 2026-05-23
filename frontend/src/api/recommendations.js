import client from './client'

export const getRecommendations = () => client.get('/recommendations/').then(r => r.data)
export const getPredictions     = () => client.get('/recommendations/predictions/').then(r => r.data)
