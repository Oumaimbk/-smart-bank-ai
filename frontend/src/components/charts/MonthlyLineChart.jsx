import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { formatCurrency, formatMonth } from '../../utils/formatters'

function pivotMonthly(raw) {
  const map = {}
  raw.forEach(({ month, direction, total }) => {
    const key = String(month).slice(0, 7)
    if (!map[key]) map[key] = { month: key, Credit: 0, Debit: 0 }
    map[key][direction] = parseFloat(total)
  })
  return Object.values(map).sort((a, b) => a.month.localeCompare(b.month))
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, padding: '10px 14px', boxShadow: '0 4px 12px rgba(0,0,0,.1)' }}>
      <div style={{ fontWeight: 700, marginBottom: 6, fontSize: 13 }}>{formatMonth(label)}</div>
      {payload.map(p => (
        <div key={p.name} style={{ display: 'flex', justifyContent: 'space-between', gap: 20, fontSize: 13 }}>
          <span style={{ color: p.color, fontWeight: 600 }}>{p.name}</span>
          <span style={{ fontWeight: 700 }}>{formatCurrency(p.value)}</span>
        </div>
      ))}
    </div>
  )
}

export default function MonthlyLineChart({ data }) {
  if (!data?.length) return <div className="empty-state"><div>Aucune donnée</div></div>
  const chartData = pivotMonthly(data)
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData} margin={{ top: 5, right: 16, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis dataKey="month" tickFormatter={formatMonth} tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis tickFormatter={v => `${(v / 1000).toFixed(0)}k`} tick={{ fontSize: 11 }} tickLine={false} axisLine={false} width={42} />
        <Tooltip content={<CustomTooltip />} />
        <Legend iconType="circle" iconSize={8} formatter={v => <span style={{ fontSize: 12 }}>{v}</span>} />
        <Line type="monotone" dataKey="Credit" stroke="#16a34a" strokeWidth={2.5} dot={false} name="Crédits" />
        <Line type="monotone" dataKey="Debit"  stroke="#dc2626" strokeWidth={2.5} dot={false} name="Débits" />
      </LineChart>
    </ResponsiveContainer>
  )
}
