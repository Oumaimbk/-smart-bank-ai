import client from './client'

export const getMLMetrics        = () => client.get('/analytics/ml-metrics/').then(r => r.data)
export const getFeatureImportance = () => client.get('/analytics/feature-importance/').then(r => r.data)
