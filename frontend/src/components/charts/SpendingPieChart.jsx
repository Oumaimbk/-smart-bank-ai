import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { categoryColor, formatCurrency } from '../../utils/formatters'

const renderLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  if (percent < 0.05) return null
  const RAD = Math.PI / 180
  const r = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + r * Math.cos(-midAngle * RAD)
  const y = cy + r * Math.sin(-midAngle * RAD)
  return (
    <text x={x} y={y} fill="#fff" textAnchor="middle" dominantBaseline="central"
      fontSize={11} fontWeight={700}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]
  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, padding: '10px 14px', boxShadow: '0 4px 12px rgba(0,0,0,.1)' }}>
      <div style={{ fontWeight: 700, marginBottom: 4 }}>{d.name}</div>
      <div style={{ color: '#64748b', fontSize: 13 }}>{formatCurrency(d.value)}</div>
    </div>
  )
}

export default function SpendingPieChart({ data }) {
  if (!data?.length) return <div className="empty-state"><div>Aucune donnée</div></div>
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={data} dataKey="total" nameKey="category"
          cx="50%" cy="50%" outerRadius={110} labelLine={false} label={renderLabel}>
          {data.map((entry, i) => (
            <Cell key={i} fill={categoryColor(entry.category)} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
        <Legend
          iconType="circle" iconSize={8}
          formatter={v => <span style={{ fontSize: 12, color: '#374151' }}>{v}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
