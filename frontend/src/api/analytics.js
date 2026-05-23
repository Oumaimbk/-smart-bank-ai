import client from './client'

export const getKPI              = () => client.get('/analytics/kpi/').then(r => r.data)
export const getSpendingByCategory = () => client.get('/analytics/spending-by-category/').then(r => r.data)
export const getMonthlyEvolution   = () => client.get('/analytics/monthly-evolution/').then(r => r.data)
export const getTopMerchants       = () => client.get('/analytics/top-merchants/').then(r => r.data)
