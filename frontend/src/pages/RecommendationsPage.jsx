import { RiLightbulbLine, RiLineChartLine } from 'react-icons/ri'
import { getRecommendations } from '../api/recommendations'
import { getPredictions }     from '../api/recommendations'
import { useApi } from '../hooks/useApi'
import Spinner from '../components/ui/Spinner'
import Alert from '../components/ui/Alert'
import Badge from '../components/ui/Badge'
import { formatCurrency, formatMonth } from '../utils/formatters'

const PRIORITY_ORDER = { high: 0, medium: 1, low: 2 }

export default function RecommendationsPage() {
  const recs  = useApi(getRecommendations)
  const preds = useApi(getPredictions)

  const sorted = recs.data
    ? [...recs.data].sort((a, b) => (PRIORITY_ORDER[a.priority] ?? 9) - (PRIORITY_ORDER[b.priority] ?? 9))
    : []

  return (
    <>
      <Alert type="error" message={recs.error || preds.error} />

      {/* Recommendations */}
      <div style={{ marginBottom: 28 }}>
        <div className="page-header" style={{ marginBottom: 16 }}>
          <div>
            <div className="page-title" style={{ fontSize: 17, display: 'flex', alignItems: 'center', gap: 8 }}>
              <RiLightbulbLine style={{ color: 'var(--warn)' }} />
              Recommandations budgétaires
            </div>
            <div className="page-subtitle">Générées par IA à partir de vos habitudes de dépenses</div>
          </div>
          {sorted.length > 0 && (
            <div style={{ display: 'flex', gap: 8 }}>
              {['high','medium','low'].map(p => {
                const count = sorted.filter(r => r.priority === p).length
                return count > 0
                  ? <Badge key={p} type={p} label={`${count} ${p === 'high' ? 'Haute' : p === 'medium' ? 'Moyenne' : 'Basse'}`} />
                  : null
              })}
            </div>
          )}
        </div>

        {recs.loading ? <Spinner /> : sorted.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💡</div>
            <div className="empty-title">Aucune recommandation</div>
            <div className="empty-text">Importez vos transactions pour générer des conseils personnalisés.</div>
          </div>
        ) : (
          <div className="rec-grid">
            {sorted.map(r => (
              <div className="rec-card" key={r.id}>
                <div className={`rec-priority-bar ${r.priority}`} />
                <div className="rec-body">
                  {r.category && <div className="rec-category">{r.category}</div>}
                  <div className="rec-message">{r.message}</div>
                  {r.reason && (
                    <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 6, fontStyle: 'italic' }}>
                      💡 {r.reason}
                    </div>
                  )}
                </div>
                <Badge type={r.priority}
                  label={r.priority === 'high' ? 'Haute' : r.priority === 'medium' ? 'Moyenne' : 'Basse'} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Predictions */}
      <div>
        <div className="page-header" style={{ marginBottom: 16 }}>
          <div>
            <div className="page-title" style={{ fontSize: 17, display: 'flex', alignItems: 'center', gap: 8 }}>
              <RiLineChartLine style={{ color: 'var(--primary)' }} />
              Prédictions — mois prochain
            </div>
            <div className="page-subtitle">Random Forest entraîné sur vos données historiques</div>
          </div>
        </div>

        <div className="card">
          <div className="card-body" style={{ padding: 0 }}>
            {preds.loading ? <Spinner /> : !preds.data?.length ? (
              <div className="empty-state">
                <div className="empty-icon">📈</div>
                <div className="empty-title">Aucune prédiction</div>
                <div className="empty-text">Les prédictions apparaîtront après le premier import.</div>
              </div>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Catégorie</th>
                      <th>Période cible</th>
                      <th style={{ textAlign: 'right' }}>Montant prédit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...preds.data]
                      .sort((a, b) => b.predicted_amount - a.predicted_amount)
                      .map(p => (
                        <tr key={p.id}>
                          <td style={{ fontWeight: 600 }}>{p.category}</td>
                          <td>
                            <span className="badge badge-blue">{formatMonth(p.target_period + '-01')}</span>
                          </td>
                          <td style={{ textAlign: 'right' }}>
                            <span className="pred-amount">{formatCurrency(p.predicted_amount)}</span>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}
