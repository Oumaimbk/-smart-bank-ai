import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Alert from '../components/ui/Alert'
import { RiBankLine } from 'react-icons/ri'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate   = useNavigate()

  const [form, setForm]       = useState({ email: '', password: '' })
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)

  const handle = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const submit = async e => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form)
      navigate('/')
    } catch (err) {
      const data = err.response?.data
      setError(data?.detail || data?.non_field_errors?.[0] || 'Email ou mot de passe incorrect.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-icon"><RiBankLine /></div>
          <div className="auth-title">BankAnalyzer</div>
          <div className="auth-subtitle">Connectez-vous à votre espace</div>
        </div>

        <Alert type="error" message={error} onClose={() => setError('')} />

        <form onSubmit={submit}>
          <div className="form-group">
            <label className="form-label">Adresse email</label>
            <input name="email" type="email" className="form-input" placeholder="vous@example.com"
              value={form.email} onChange={handle} required autoFocus />
          </div>
          <div className="form-group">
            <label className="form-label">Mot de passe</label>
            <input name="password" type="password" className="form-input" placeholder="••••••••"
              value={form.password} onChange={handle} required />
          </div>
          <button type="submit" className="btn btn-primary btn-full" disabled={loading}
            style={{ marginTop: 8 }}>
            {loading ? 'Connexion…' : 'Se connecter'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 13, color: 'var(--text-muted)' }}>
          Pas encore de compte ?{' '}
          <Link to="/register" style={{ color: 'var(--primary)', fontWeight: 600 }}>
            Créer un compte
          </Link>
        </p>
      </div>
    </div>
  )
}
