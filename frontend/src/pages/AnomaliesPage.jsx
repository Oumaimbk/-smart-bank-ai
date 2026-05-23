import { useState } from 'react'
import { RiArrowLeftSLine, RiArrowRightSLine, RiShieldLine } from 'react-icons/ri'
import { getAnomalies, getAnomalySummary } from '../api/anomalies'
import { useApi } from '../hooks/useApi'
import Spinner from '../components/ui/Spinner'
import Alert from '../components/ui/Alert'
import { formatCurrency, formatDate } from '../utils/formatters'

const TYPE_META = {
  // Legacy types (backward compat)
  high_amount:        { label: 'Montant élevé',         cls: 'chip-high-amount',   emoji: '🔴' },
  odd_hour:           { label: 'Heure inhabituelle',    cls: 'chip-odd-hour',      emoji: '🕐' },
  category_spike:     { label: 'Pic catégorie',         cls: 'chip-category-spike',emoji: '📈' },
  unusual_frequency:  { label: 'Fréquence anormale',   cls: 'chip-odd-hour',      emoji: '⚡' },
  // New unified types
  ml_isolation_forest:{ label: 'Schéma inhabituel (IF)',cls: 'chip-category-spike',emoji: '🤖' },
  rule_high_amount:   { label: 'Montant élevé (règle)', cls: 'chip-high-amount',   emoji: '🔴' },
  rule_odd_hour:      { label: 'Heure suspecte (règle)',cls: 'chip-odd-hour',      emoji: '🕐' },
}

const PAGE_SIZE = 50

export default function AnomaliesPage() {
  const [page, setPage]   = useState(1)
  const [filter, setFilter] = useState('')

  const summary = useApi(getAnomalySummary)
  const { data, loading, error } = useApi(
    () => getAnomalies(page, filter || undefined),
    [page, filter]
  )

  const rows = data?.results ?? []
  const totalPages = data ? Math.ceil(data.count / PAGE_SIZE) : 1

  const handleFilter = val => { setFilter(val); setPage(1) }

  return (
    <>
      <Alert type="error" message={error || summary.error} />

      {/* Summary KPIs */}
      {!summary.loading && summary.data && (
        <div className="kpi-grid" style={{ marginBottom: 24 }}>
          <div className="kpi-card">
            <div className="kpi-icon" style={{ background: '#fff7ed', color: '#c2410c' }}>
              <RiShieldLine />
            </div>
            <div className="kpi-info">
              <div className="kpi-label">Total anomalies</div>
              <div className="kpi-value">{summary.data.total}</div>
              <div className="kpi-sub">Toutes transactions suspectes</div>
            </div>
          </div>
          {Object.entries(summary.data.by_type).map(([type, count]) => {
            const meta = TYPE_META[type] ?? { label: type, emoji: '⚠️' }
            return (
              <div
                key={type}
                className="kpi-card"
                style={{ cursor: 'pointer', border: filter === type ? '2px solid var(--primary)' : undefined }}
                onClick={() => handleFilter(filter === type ? '' : type)}
              >
                <div className="kpi-icon" style={{ background: '#fff7ed', color: '#c2410c', fontSize: 22 }}>
                  {meta.emoji}
                </div>
                <div className="kpi-info">
                  <div className="kpi-label">{meta.label}</div>
                  <div className="kpi-value">{count}</div>
                  <div className="kpi-sub" style={{ color: 'var(--primary)', fontSize: 11 }}>
                    {filter === type ? 'Filtre actif — cliquer pour retirer' : 'Cliquer pour filtrer'}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Transactions anormales</div>
            {data && <div className="card-subtitle">{data.count} résultat{data.count > 1 ? 's' : ''}{filter ? ` · filtre: ${TYPE_META[filter]?.label}` : ''}</div>}
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            {filter && (
              <button className="btn btn-sm btn-outline" onClick={() => handleFilter('')}>
                Tout afficher
              </button>
            )}
            <select className="form-input" style={{ maxWidth: 200 }} value={filter}
              onChange={e => handleFilter(e.target.value)}>
              <option value="">Tous les types</option>
              {Object.entries(TYPE_META).map(([k, v]) => (
                <option key={k} value={k}>{v.emoji} {v.label}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="card-body" style={{ padding: 0 }}>
          {loading ? <Spinner /> : rows.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">✅</div>
              <div className="empty-title">Aucune anomalie</div>
              <div className="empty-text">Aucune transaction suspecte pour ce filtre.</div>
            </div>
          ) : (
            <>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>ID Transaction</th>
                      <th>Catégorie</th>
                      <th>Marchand</th>
                      <th>Type</th>
                      <th style={{ textAlign: 'right' }}>Montant</th>
                      <th>Score</th>
                      <th>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map(a => {
                      const meta = TYPE_META[a.anomaly_type] ?? { label: a.anomaly_type, cls: 'chip-odd-hour' }
                      const scoreWidth = Math.min(100, (a.score / 10) * 100)
                      return (
                        <tr key={a.id}>
                          <td style={{ whiteSpace: 'nowrap', fontSize: 13, color: 'var(--text-muted)' }}>
                            {formatDate(a.transaction_date)}
                          </td>
                          <td style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--text-muted)' }}>
                            {a.transaction_id}
                          </td>
                          <td style={{ fontSize: 13 }}>{a.category}</td>
                          <td style={{ fontSize: 13 }}>{a.merchant_name || '—'}</td>
                          <td><span className={`chip ${meta.cls}`}>{meta.label}</span></td>
                          <td style={{ textAlign: 'right', fontWeight: 700, color: 'var(--debit)' }}>
                            {formatCurrency(a.amount)}
                          </td>
                          <td style={{ minWidth: 120 }}>
                            <div className="score-bar-wrap">
                              <div className="score-bar">
                                <div className="score-bar-fill" style={{ width: `${scoreWidth}%` }} />
                              </div>
                              <span className="score-label">{Number(a.score).toFixed(1)}</span>
                            </div>
                          </td>
                          <td style={{ fontSize: 12, color: 'var(--text-muted)', maxWidth: 260 }}>
                            <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {a.description}
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              {totalPages > 1 && (
                <div className="pagination" style={{ padding: '14px 22px' }}>
                  <span className="pagination-info">Page {page} sur {totalPages} — {data.count} résultats</span>
                  <div className="pagination-controls">
                    <button className="page-btn" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
                      <RiArrowLeftSLine />
                    </button>
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      const p = Math.max(1, Math.min(page - 2, totalPages - 4)) + i
                      return (
                        <button key={p} className={`page-btn${p === page ? ' active' : ''}`} onClick={() => setPage(p)}>
                          {p}
                        </button>
                      )
                    })}
                    <button className="page-btn" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
                      <RiArrowRightSLine />
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  )
}
