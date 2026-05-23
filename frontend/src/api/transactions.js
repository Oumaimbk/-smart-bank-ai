import client from './client'

export const uploadCSV = formData => client.post('/transactions/upload/', formData).then(r => r.data)

export const getTransactions = ({ page = 1, direction, search } = {}) =>
  client.get('/transactions/', {
    params: {
      page,
      ...(direction ? { direction } : {}),
      ...(search    ? { search }    : {}),
    },
  }).then(r => r.data)

export const getBatches        = () => client.get('/transactions/batches/').then(r => r.data)
export const getUploadBatches  = () => client.get('/transactions/batches/').then(r => r.data)
export const deleteUploadBatch = (batchId) =>
  client.delete(`/transactions/batches/${batchId}/delete/`).then(r => r.data)
