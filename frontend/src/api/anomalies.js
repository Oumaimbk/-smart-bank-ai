import client from './client'

export const getAnomalies       = (page = 1, anomaly_type) =>
  client.get('/anomalies/', { params: { page, ...(anomaly_type ? { anomaly_type } : {}) } }).then(r => r.data)

export const getAnomalySummary  = () => client.get('/anomalies/summary/').then(r => r.data)
