import { useState } from 'react'
import { RiArrowLeftSLine, RiArrowRightSLine, RiAlertLine, RiSearchLine } from 'react-icons/ri'
import { getTransactions } from '../api/transactions'
import { useApi } from '../hooks/useApi'
import Spinner from '../components/ui/Spinner'
import Alert from '../components/ui/Alert'
import Badge from '../components/ui/Badge'
import { formatCurrency, formatDate, categoryColor } from '../utils/formatters'

const PAGE_SIZE = 50

export default function TransactionsPage() {
  const [page, setPage]               = useState(1)
  const [search, setSearch]           = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [direction, setDirection]     = useState('')

  const { data, loading, error } = useApi(
    () => getTransactions({ page, search, direction }),
    [page, search, direction]
  )

  const applySearch = () => { setSearch(searchInput); setPage(1) }
  const handleKey   = e => { if (e.key === 'Enter') applySearch() }
  const handleDir   = val => { setDirection(val); setPage(1) }

  const rows = data?.results ?? []
  const totalPages = data ? Math.ceil(data.count / PAGE_SIZE) : 1

  return (
    <>
      <Alert type="error" message={error} />

      {/* Filter bar — server-side */}
      <div className="filter-bar">
        <div style={{ display: 'flex', gap: 0, flex: 1, maxWidth: 360 }}>
          <input className="form-input" placeholder="Rechercher narration, marchand, ID…"
            value={searchInput} onChange={e => setSearchInput(e.target.value)} onKeyDown={handleKey}
            style={{ borderRadius: '6px 0 0 6px', flex: 1 }} />
          <button className="btn btn-primary" onClick={applySearch}
            style={{ borderRadius: '0 6px 6px 0', padding: '0 12px' }}>
            <RiSearchLine />
          </button>
        </div>

        <select className="form-input" value={direction} onChange={e => handleDir(e.target.value)}>
          <option value="">Toutes directions</option>
          <option value="Credit">Crédits</option>
          <option value="Debit">Débits</option>
        </select>

        {data && (
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            {data.count.toLocaleString()} transaction{data.count > 1 ? 's' : ''}
          </span>
        )}

        {(search || direction) && (
          <button className="btn btn-sm btn-outline"
            onClick={() => { setSearch(''); setSearchInput(''); setDirection(''); setPage(1) }}>
            Réinitialiser
          </button>
        )}
      </div>

      <div className="card">
        {loading ? <Spinner /> : (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Date</th><th>ID</th><th>Narration</th><th>Marchand</th>
                    <th>Catégorie</th><th>Direction</th>
                    <th style={{ textAlign: 'right' }}>Montant</th>
                    <th style={{ textAlign: 'right' }}>Solde après</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {rows.length === 0 ? (
                    <tr><td colSpan={9} style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>Aucun résultat</td></tr>
                  ) : rows.map(t => (
                    <tr key={t.id}>
                      <td style={{ whiteSpace: 'nowrap', color: 'var(--text-muted)', fontSize: 13 }}>{formatDate(t.transaction_date)}</td>
                      <td style={{ fontFamily: 'monospace', fontSize: 11, color: 'var(--text-muted)' }}>{t.transaction_id}</td>
                      <td style={{ maxWidth: 200 }}>
                        <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: 13 }}>{t.narration || '—'}</div>
                      </td>
                      <td style={{ fontSize: 13 }}>{t.merchant_name || '—'}</td>
                      <td>
                        <span style={{
                          display: 'inline-block', padding: '2px 8px', borderRadius: 12,
                          fontSize: 11, fontWeight: 700,
                          background: categoryColor(t.category) + '22',
                          color: categoryColor(t.category),
                        }}>{t.category || '—'}</span>
                      </td>
                      <td>
                        <Badge type={t.direction === 'Credit' ? 'credit' : 'debit'}
                          label={t.direction === 'Credit' ? 'Crédit' : 'Débit'} />
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 700, color: t.direction === 'Credit' ? 'var(--credit)' : 'var(--debit)' }}>
                        {t.direction === 'Credit' ? '+' : '−'}{formatCurrency(t.amount)}
                      </td>
                      <td style={{ textAlign: 'right', fontSize: 13, color: 'var(--text-muted)' }}>
                        {t.balance_after != null ? formatCurrency(t.balance_after) : '—'}
                      </td>
                      <td>{t.is_anomalous && <span title="Anormale" style={{ color: 'var(--warn)', fontSize: 16 }}><RiAlertLine /></span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="pagination" style={{ padding: '14px 22px' }}>
              <span className="pagination-info">Page {page} / {totalPages} — {data?.count?.toLocaleString() ?? 0} résultats</span>
              <div className="pagination-controls">
                <button className="page-btn" disabled={page <= 1} onClick={() => setPage(p => p - 1)}><RiArrowLeftSLine /></button>
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const p = Math.max(1, Math.min(page - 2, totalPages - 4)) + i
                  return <button key={p} className={`page-btn${p === page ? ' active' : ''}`} onClick={() => setPage(p)}>{p}</button>
                })}
                <button className="page-btn" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}><RiArrowRightSLine /></button>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  )
}
