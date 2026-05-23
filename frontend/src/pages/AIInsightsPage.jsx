import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'
import { RiBrainLine, RiBarChart2Line, RiCheckboxCircleLine } from 'react-icons/ri'
import { getMLMetrics, getFeatureImportance } from '../api/mlInsights'
import { useApi } from '../hooks/useApi'
import Spinner from '../components/ui/Spinner'
import Alert from '../components/ui/Alert'

const PALETTE = ['#2563eb', '#16a34a', '#d97706', '#7c3aed', '#0891b2', '#db2777']

/* ── small helpers ── */
function MetricBadge({ label, value, good }) {
  const color = good === undefined ? '#2563eb' : good ? '#16a34a' : '#d97706'
  return (
    <div style={{ textAlign: 'center', padding: '12px 18px', background: '#f8fafc', borderRadius: 10, flex: 1, minWidth: 120 }}>
      <div style={{ fontSize: 22, fontWeight: 800, color }}>{value ?? '—'}</div>
      <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{label}</div>
    </div>
  )
}

function ModelCard({ record }) {
  const m = record.metrics ?? {}
  const isRegressor = record.model_name === 'random_forest'
  const fewSamples  = isRegressor && (record.sample_count ?? 0) < 10

  return (
    <div className="card" style={{ marginBottom: 20 }}>
      <div className="card-header">
        <div>
          <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <RiBrainLine style={{ color: '#7c3aed' }} />
            {record.display_name}
          </div>
          <div className="card-subtitle">{record.task}</div>
        </div>
        <div style={{ fontSize: 12, color: '#94a3b8' }}>
          {record.sample_count} échantillons · évalué {record.computed_at
            ? new Date(record.computed_at).toLocaleDateString('fr-MA')
            : '—'}
        </div>
      </div>
      <div className="card-body">
        {fewSamples ? (
          <div style={{
            background: '#f8fafc', border: '1px solid #e2e8f0',
            borderRadius: 8, padding: '14px 18px',
            display: 'flex', alignItems: 'flex-start', gap: 12,
          }}>
            <span style={{ fontSize: 20 }}>&#x2139;&#xFE0F;</span>
            <div>
              <div style={{ fontWeight: 600, color: '#475569', marginBottom: 4 }}>
                Evaluation limitee — seulement {record.sample_count} echantillon{record.sample_count > 1 ? 's' : ''} disponible{record.sample_count > 1 ? 's' : ''}
              </div>
              <div style={{ fontSize: 13, color: '#64748b', lineHeight: 1.6 }}>
                Le Random Forest est evalue sur un holdout 20 % des agregats mensuels.
                Avec peu de donnees historiques, ce score n'est pas representatif.
                Uploadez plus de mois de transactions pour obtenir une evaluation fiable.
              </div>
              {Object.keys(m).length > 0 && (
                <div style={{ marginTop: 10, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                  {m.mae  != null && <span style={{ fontSize: 12, color: '#94a3b8' }}>MAE: {m.mae?.toLocaleString('fr-MA')} MAD</span>}
                  {m.rmse != null && <span style={{ fontSize: 12, color: '#94a3b8' }}>RMSE: {m.rmse?.toLocaleString('fr-MA')} MAD</span>}
                  {m.r2   != null && <span style={{ fontSize: 12, color: '#94a3b8' }}>R2: {m.r2}</span>}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            {isRegressor ? (
              <>
                <MetricBadge label="MAE (MAD)" value={m.mae?.toLocaleString('fr-MA')} />
                <MetricBadge label="RMSE (MAD)" value={m.rmse?.toLocaleString('fr-MA')} />
                <MetricBadge label="R2 Score" value={m.r2} good={m.r2 >= 0.7} />
              </>
            ) : (
              <>
                <MetricBadge label="Accuracy" value={m.accuracy ? `${(m.accuracy * 100).toFixed(1)} %` : '—'} good={m.accuracy >= 0.8} />
                <MetricBadge label="F1 (weighted)" value={m.f1_weighted?.toFixed(4)} good={m.f1_weighted >= 0.8} />
                <MetricBadge label="F1 (macro)" value={m.f1_macro?.toFixed(4)} good={m.f1_macro >= 0.8} />
                <MetricBadge label="Precision" value={m.precision?.toFixed(4)} good={m.precision >= 0.8} />
                <MetricBadge label="Rappel" value={m.recall?.toFixed(4)} good={m.recall >= 0.8} />
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default function AIInsightsPage() {
  const metrics    = useApi(getMLMetrics)
  const importance = useApi(getFeatureImportance)

  const models    = metrics.data?.models ?? []
  const features  = importance.data?.features ?? []
  const impModel  = importance.data?.model ?? 'Random Forest Regressor'
  const impDate   = importance.data?.computed_at
    ? new Date(importance.data.computed_at).toLocaleDateString('fr-MA')
    : null

  return (
    <>
      <Alert type="error" message={metrics.error || importance.error} />

      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ fontSize: 20, fontWeight: 800, display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
          <RiBrainLine style={{ color: '#7c3aed', fontSize: 24 }} />
          AI Insights
        </div>
        <div style={{ color: '#64748b', fontSize: 14 }}>
          Métriques d'évaluation et explicabilité des modèles de Machine Learning
        </div>
      </div>

      {/* Pipeline overview */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div className="card-title">Pipeline ML — Vue d'ensemble</div>
        </div>
        <div className="card-body">
          <div style={{ display: 'flex', gap: 0, overflowX: 'auto' }}>
            {[
              { step: '1', label: 'TF-IDF + LR', desc: 'Catégorisation', color: '#2563eb' },
              { step: '2', label: 'Isolation Forest', desc: 'Détection d\'anomalies', color: '#db2777' },
              { step: '3', label: 'Random Forest', desc: 'Prévision mensuelle', color: '#16a34a' },
              { step: '4', label: 'Moteur règles', desc: 'Recommandations', color: '#d97706' },
            ].map((s, i, arr) => (
              <div key={s.step} style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{ textAlign: 'center', padding: '12px 16px', minWidth: 130 }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: '50%', background: s.color,
                    color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 700, margin: '0 auto 8px',
                  }}>{s.step}</div>
                  <div style={{ fontWeight: 700, fontSize: 13 }}>{s.label}</div>
                  <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>{s.desc}</div>
                </div>
                {i < arr.length - 1 && (
                  <div style={{ color: '#cbd5e1', fontSize: 20, padding: '0 4px' }}>→</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Model metrics */}
      <div style={{ marginBottom: 8 }}>
        <div style={{ fontWeight: 700, fontSize: 15, display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
          <RiCheckboxCircleLine style={{ color: '#16a34a' }} />
          Métriques d'évaluation par modèle
        </div>
        {metrics.loading ? <Spinner /> : models.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <div className="empty-title">Aucune métrique disponible</div>
            <div className="empty-text">Importez un fichier CSV pour déclencher l'entraînement et l'évaluation des modèles.</div>
          </div>
        ) : (
          models.map(record => <ModelCard key={record.model_name} record={record} />)
        )}
      </div>

      {/* Feature importance */}
      <div className="card" style={{ marginTop: 8 }}>
        <div className="card-header">
          <div>
            <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <RiBarChart2Line style={{ color: '#16a34a' }} />
              Importance des variables — {impModel}
            </div>
            <div className="card-subtitle">
              Contribution de chaque feature aux prédictions de dépenses
              {impDate ? ` · calculé le ${impDate}` : ''}
            </div>
          </div>
        </div>
        <div className="card-body">
          {importance.loading ? <Spinner /> : features.length === 0 ? (
            <div className="empty-state" style={{ padding: 32 }}>
              <div className="empty-icon">📈</div>
              <div className="empty-title">Pas encore disponible</div>
              <div className="empty-text">Les importances seront calculées après le premier import CSV.</div>
            </div>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={features} layout="vertical" margin={{ left: 16, right: 32, top: 8, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis
                    type="number"
                    domain={[0, 1]}
                    tickFormatter={v => `${(v * 100).toFixed(0)} %`}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis type="category" dataKey="feature" width={130} tick={{ fontSize: 12 }} />
                  <Tooltip
                    formatter={(v, name) => [`${(v * 100).toFixed(1)} %`, 'Importance']}
                    labelStyle={{ fontWeight: 700 }}
                  />
                  <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                    {features.map((_, i) => (
                      <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>

              <div className="table-wrap" style={{ marginTop: 16 }}>
                <table>
                  <thead>
                    <tr>
                      <th style={{ width: 40 }}>#</th>
                      <th>Variable</th>
                      <th style={{ textAlign: 'right' }}>Importance</th>
                      <th style={{ textAlign: 'right' }}>%</th>
                    </tr>
                  </thead>
                  <tbody>
                    {features.map(f => (
                      <tr key={f.feature}>
                        <td style={{ color: '#94a3b8', fontWeight: 700 }}>{f.rank}</td>
                        <td style={{ fontWeight: 600 }}>{f.feature}</td>
                        <td style={{ textAlign: 'right', fontFamily: 'monospace' }}>{f.importance.toFixed(4)}</td>
                        <td style={{ textAlign: 'right', color: '#2563eb', fontWeight: 700 }}>{f.importance_pct} %</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Anomaly detection explanation */}
      <div className="card" style={{ marginTop: 20 }}>
        <div className="card-header">
          <div className="card-title">Détection de schémas de dépenses inhabituels</div>
          <div className="card-subtitle">Deux méthodes complémentaires activées simultanément</div>
        </div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div style={{ background: '#fdf4ff', borderRadius: 10, padding: 16, borderLeft: '4px solid #7c3aed' }}>
              <div style={{ fontWeight: 700, color: '#7c3aed', marginBottom: 6 }}>🤖 Isolation Forest (ML)</div>
              <div style={{ fontSize: 13, color: '#475569', lineHeight: 1.6 }}>
                Modèle non supervisé entraîné sur 4 features : montant, heure,
                week-end, catégorie. Identifie les transactions qui s'écartent
                statistiquement du comportement normal (contamination = 5 %).
              </div>
              <div style={{ marginTop: 8, fontSize: 12, color: '#7c3aed', fontWeight: 600 }}>
                Type : <code>ml_isolation_forest</code>
              </div>
            </div>
            <div style={{ background: '#fff7ed', borderRadius: 10, padding: 16, borderLeft: '4px solid #d97706' }}>
              <div style={{ fontWeight: 700, color: '#d97706', marginBottom: 6 }}>📏 Règles statistiques</div>
              <div style={{ fontSize: 13, color: '#475569', lineHeight: 1.6 }}>
                <strong>Montant élevé :</strong> z-score &gt; 2.5 par rapport à la moyenne de la catégorie.
                <br />
                <strong>Heure inhabituelle :</strong> transaction entre 00h et 05h59.
              </div>
              <div style={{ marginTop: 8, fontSize: 12, color: '#d97706', fontWeight: 600 }}>
                Types : <code>rule_high_amount</code> · <code>rule_odd_hour</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
