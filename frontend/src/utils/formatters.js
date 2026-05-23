const MAD = new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD', minimumFractionDigits: 2 })
const NUM = new Intl.NumberFormat('fr-MA')

export const formatCurrency = v => MAD.format(Number(v))
export const formatNumber   = v => NUM.format(Number(v))

export const formatDate = dateStr => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('fr-MA', { day: '2-digit', month: 'short', year: 'numeric' })
}

export const formatMonth = dateStr => {
  if (!dateStr) return ''
  const [y, m] = dateStr.slice(0, 7).split('-')
  const months = ['Jan','Fév','Mar','Avr','Mai','Juin','Juil','Août','Sep','Oct','Nov','Déc']
  return `${months[parseInt(m, 10) - 1]} ${y}`
}

export const fileSize = bytes => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

// Stable color palette for categories
const PALETTE = [
  '#2563eb','#16a34a','#dc2626','#d97706','#7c3aed',
  '#0891b2','#db2777','#65a30d','#0f766e','#c2410c',
  '#4338ca','#94a3b8',
]
const _map = {}
let _idx = 0

export const categoryColor = cat => {
  if (!_map[cat]) { _map[cat] = PALETTE[_idx % PALETTE.length]; _idx++ }
  return _map[cat]
}
