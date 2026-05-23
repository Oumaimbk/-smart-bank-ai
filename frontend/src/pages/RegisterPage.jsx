import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Alert from '../components/ui/Alert'
import { RiBankLine } from 'react-icons/ri'

export default function RegisterPage() {
  const { register, login } = useAuth()
  const navigate = useNavigate()

  const [form, setForm]       = useState({ username: '', email: '', password: '', password2: '' })
  const [errors, setErrors]   = useState({})
  const [loading, setLoading] = useState(false)
  const [globalErr, setGlobalErr] = useState('')

  const handle = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const submit = async e => {
    e.preventDefault()
    setErrors({})
    setGlobalErr('')
    setLoading(true)
    try {
      await register(form)
      // Auto-login after registration
      await login({ email: form.email, password: form.password })
      navigate('/')
    } catch (err) {
      const data = err.response?.data
      if (data && typeof data === 'object') {
        if (data.detail) setGlobalErr(data.detail)
        else setErrors(data)
      } else {
        setGlobalErr('Une erreur est survenue.')
      }
    } finally {
      setLoading(false)
    }
  }

  const f = name => (
    <>
      {errors[name] && <div className="form-error">{errors[name][0]}</div>}
    </>
  )

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-icon"><RiBankLine /></div>
          <div className="auth-title">Créer un compte</div>
          <div className="auth-subtitle">Commencez à analyser vos finances</div>
        </div>

        <Alert type="error" message={globalErr} onClose={() => setGlobalErr('')} />

        <form onSubmit={submit}>
          <div className="form-group">
            <label className="form-label">Nom d'utilisateur</label>
            <input name="username" className={`form-input${errors.username ? ' error' : ''}`}
              placeholder="john_doe" value={form.username} onChange={handle} required />
            {f('username')}
          </div>
          <div className="form-group">
            <label className="form-label">Adresse email</label>
            <input name="email" type="email" className={`form-input${errors.email ? ' error' : ''}`}
              placeholder="vous@example.com" value={form.email} onChange={handle} required />
            {f('email')}
          </div>
          <div className="form-group">
            <label className="form-label">Mot de passe</label>
            <input name="password" type="password" className={`form-input${errors.password ? ' error' : ''}`}
              placeholder="Min. 8 caractères" value={form.password} onChange={handle} required />
            {f('password')}
          </div>
          <div className="form-group">
            <label className="form-label">Confirmer le mot de passe</label>
            <input name="password2" type="password" className={`form-input${errors.password2 ? ' error' : ''}`}
              placeholder="••••••••" value={form.password2} onChange={handle} required />
            {f('password2')}
          </div>
          <button type="submit" className="btn btn-primary btn-full" disabled={loading}
            style={{ marginTop: 8 }}>
            {loading ? 'Création…' : 'Créer mon compte'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: 13, color: 'var(--text-muted)' }}>
          Déjà un compte ?{' '}
          <Link to="/login" style={{ color: 'var(--primary)', fontWeight: 600 }}>Se connecter</Link>
        </p>
      </div>
    </div>
  )
}
