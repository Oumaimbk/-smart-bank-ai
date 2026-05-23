export default function KPICard({ icon: Icon, label, value, sub, color = 'blue' }) {
  const strLen = value ? String(value).length : 0
  const fontSize = value && strLen > 14 ? '0.88rem'
                 : value && strLen > 11 ? '1rem'
                 : '1.25rem'

  return (
    <div className="kpi-card">
      <div className={`kpi-icon ${color}`}>
        {Icon && <Icon />}
      </div>
      <div className="kpi-info">
        <div className="kpi-label">{label}</div>
        <div
          className="kpi-value"
          title={value ?? '—'}
          style={{
            fontSize,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            maxWidth: '100%',
          }}
        >
          {value ?? '—'}
        </div>
        {sub && <div className="kpi-sub">{sub}</div>}
      </div>
    </div>
  )
}
