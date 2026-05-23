import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  RiUploadCloud2Line, RiFileLine, RiCheckboxCircleLine,
  RiDeleteBin2Line, RiAlertLine,
} from 'react-icons/ri'
import { uploadCSV, getBatches, deleteUploadBatch } from '../api/transactions'
import { useApi }    from '../hooks/useApi'
import Alert from '../components/ui/Alert'
import Spinner from '../components/ui/Spinner'
import { fileSize, formatDate } from '../utils/formatters'

const STATUS_BADGE = {
  completed:  { cls: 'badge-credit',  label: 'Complété' },
  failed:     { cls: 'badge-debit',   label: 'Échoué' },
  processing: { cls: 'badge-blue',    label: 'En cours' },
  pending:    { cls: 'badge-gray',    label: 'En attente' },
}

export default function UploadPage() {
  const navigate    = useNavigate()
  const inputRef    = useRef()
  const [file, setFile]           = useState(null)
  const [dragOver, setDragOver]   = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult]       = useState(null)
  const [error, setError]         = useState('')

  // Delete state
  const [confirmBatch, setConfirmBatch] = useState(null)  // batch object pending confirm
  const [deleting, setDeleting]         = useState(false)
  const [deleteMsg, setDeleteMsg]       = useState('')

  const { data: batches, loading: bLoading, refetch } = useApi(getBatches)

  const pickFile = f => {
    if (!f || !f.name.endsWith('.csv')) { setError('Seuls les fichiers .csv sont acceptés.'); return }
    if (f.size > 10 * 1024 * 1024) { setError('Fichier trop volumineux (max 10 MB).'); return }
    setFile(f); setResult(null); setError('')
  }

  const onDrop = e => {
    e.preventDefault(); setDragOver(false)
    pickFile(e.dataTransfer.files[0])
  }

  const submit = async () => {
    if (!file) return
    setUploading(true); setError(''); setResult(null)
    const fd = new FormData()
    fd.append('file', file)
    try {
      const res = await uploadCSV(fd)
      setResult(res)
      setFile(null)
      refetch()
    } catch (err) {
      setError(err.response?.data?.error || 'Échec de l\'import.')
    } finally {
      setUploading(false)
    }
  }

  const confirmDelete = (batch) => {
    setConfirmBatch(batch)
    setDeleteMsg('')
  }

  const cancelDelete = () => setConfirmBatch(null)

  const handleDelete = async () => {
    if (!confirmBatch) return
    setDeleting(true)
    try {
      const res = await deleteUploadBatch(confirmBatch.id)
      setDeleteMsg(`${res.deleted_transactions} transaction(s) supprimée(s).`)
      setConfirmBatch(null)
      refetch()
    } catch (err) {
      setError(err.response?.data?.error || 'Échec de la suppression.')
      setConfirmBatch(null)
    } finally {
      setDeleting(false)
    }
  }

  const batchRows = batches?.results ?? (Array.isArray(batches) ? batches : [])

  return (
    <>
      <Alert type="error"   message={error}     onClose={() => setError('')} />
      {deleteMsg && (
        <Alert type="success" message={deleteMsg} onClose={() => setDeleteMsg('')} />
      )}

      {/* Delete confirmation modal */}
      {confirmBatch && (
        <div style={{
          position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.45)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
        }}>
          <div style={{
            background: 'var(--surface)', borderRadius: 12, padding: '28px 32px',
            maxWidth: 420, width: '90%', boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
              <RiAlertLine style={{ color: 'var(--debit)', fontSize: 24 }} />
              <span style={{ fontWeight: 700, fontSize: 16 }}>Supprimer ce fichier ?</span>
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 8 }}>
              <strong>{confirmBatch.filename}</strong>
            </p>
            <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 24 }}>
              Cette action supprimera <strong>{confirmBatch.transaction_count} transaction(s)</strong> et ne peut pas être annulée.
            </p>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button className="btn btn-ghost" onClick={cancelDelete} disabled={deleting}>
                Annuler
              </button>
              <button
                className="btn btn-danger"
                onClick={handleDelete}
                disabled={deleting}
                style={{ background: 'var(--debit)', color: '#fff', border: 'none' }}
              >
                {deleting
                  ? <><div className="spinner spinner-sm" /> Suppression…</>
                  : <><RiDeleteBin2Line /> Supprimer</>
                }
              </button>
            </div>
          </div>
        </div>
      )}

      {result && (
        <div className="upload-result">
          <div className="upload-result-title">
            <RiCheckboxCircleLine style={{ verticalAlign: 'middle', marginRight: 6 }} />
            Import réussi !
          </div>
          <div className="upload-result-grid">
            {[
              ['Nouvelles transactions', result.new_transactions],
              ['Doublons ignorés',       result.skipped_duplicates],
              ['Anomalies détectées',    result.anomalies_detected],
              ['Prédictions générées',   result.predictions_generated],
              ['Recommandations',        result.recommendations_generated],
            ].map(([label, val]) => (
              <div className="upload-result-item" key={label}>
                <div className="upload-result-value">{val}</div>
                <div className="upload-result-label">{label}</div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 16, display: 'flex', gap: 10 }}>
            <button className="btn btn-primary btn-sm" onClick={() => navigate('/')}>Voir le dashboard</button>
            <button className="btn btn-outline btn-sm" onClick={() => navigate('/anomalies')}>Voir les anomalies</button>
          </div>
        </div>
      )}

      {/* Upload zone */}
      <div className="card" style={{ marginBottom: 24 }}>
        <div className="card-header">
          <div className="card-title">Importer un fichier CSV</div>
        </div>
        <div className="card-body">
          <div
            className={`upload-zone ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
          >
            <input ref={inputRef} type="file" accept=".csv" style={{ display: 'none' }}
              onChange={e => pickFile(e.target.files[0])} />

            {file ? (
              <>
                <div className="upload-icon" style={{ color: 'var(--credit)' }}><RiFileLine /></div>
                <div className="upload-title" style={{ color: 'var(--credit)' }}>Fichier prêt</div>
                <div className="upload-file-info">
                  <span className="upload-filename">{file.name}</span>
                  <span className="upload-filesize">{fileSize(file.size)}</span>
                </div>
              </>
            ) : (
              <>
                <div className="upload-icon"><RiUploadCloud2Line /></div>
                <div className="upload-title">Glissez votre fichier CSV ici</div>
                <div className="upload-sub">ou cliquez pour parcourir • Max 10 MB</div>
              </>
            )}
          </div>

          {file && (
            <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
              <button className="btn btn-primary" onClick={submit} disabled={uploading}>
                {uploading ? <><div className="spinner spinner-sm" /> Analyse en cours…</> : <><RiUploadCloud2Line />Uploader et analyser</>}
              </button>
              <button className="btn btn-ghost" onClick={() => { setFile(null); setError('') }}>Annuler</button>
            </div>
          )}

          <div className="alert alert-info" style={{ marginTop: 20, marginBottom: 0 }}>
            <RiFileLine style={{ flexShrink: 0 }} />
            <span>Colonnes requises: <strong>transaction_id, transaction_date, direction, amount</strong>. Colonnes optionnelles: customer_id, narration, merchant_name, merchant_city, payment_method, balance_after.</span>
          </div>
        </div>
      </div>

      {/* History */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">Historique des imports</div>
          <div className="card-subtitle" style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            Cliquez sur la corbeille pour supprimer un import et toutes ses transactions
          </div>
        </div>
        <div className="card-body" style={{ padding: 0 }}>
          {bLoading ? <Spinner /> : !batchRows.length ? (
            <div className="empty-state"><div className="empty-title">Aucun import</div></div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Fichier</th>
                    <th>Statut</th>
                    <th>Transactions</th>
                    <th>Date</th>
                    <th>Erreur</th>
                    <th style={{ textAlign: 'center', width: 60 }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {batchRows.map(b => {
                    const s = STATUS_BADGE[b.status] ?? STATUS_BADGE.pending
                    return (
                      <tr key={b.id}>
                        <td style={{ fontWeight: 600 }}>{b.filename}</td>
                        <td><span className={`badge ${s.cls}`}>{s.label}</span></td>
                        <td>{b.transaction_count}</td>
                        <td>{formatDate(b.created_at)}</td>
                        <td style={{ color: 'var(--debit)', fontSize: 12 }}>{b.error_message || '—'}</td>
                        <td style={{ textAlign: 'center' }}>
                          <button
                            title="Supprimer ce batch"
                            onClick={() => confirmDelete(b)}
                            style={{
                              background: 'none', border: 'none', cursor: 'pointer',
                              color: '#ef4444', fontSize: 18, padding: '4px 8px',
                              borderRadius: 6, transition: 'background .15s',
                            }}
                            onMouseEnter={e => e.currentTarget.style.background = '#fee2e2'}
                            onMouseLeave={e => e.currentTarget.style.background = 'none'}
                          >
                            <RiDeleteBin2Line />
                          </button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
