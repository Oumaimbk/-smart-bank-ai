import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import {
  RiDashboardLine, RiUploadCloud2Line, RiListUnordered,
  RiAlertLine, RiLightbulbLine, RiLogoutBoxLine, RiBankLine, RiBrainLine,
} from 'react-icons/ri'

const NAV = [
  { to: '/',               icon: RiDashboardLine,     label: 'Dashboard' },
  { to: '/upload',         icon: RiUploadCloud2Line,   label: 'Upload CSV' },
  { to: '/transactions',   icon: RiListUnordered,      label: 'Transactions' },
  { to: '/anomalies',      icon: RiAlertLine,          label: 'Anomalies' },
  { to: '/recommendations',icon: RiLightbulbLine,      label: 'Recommandations' },
  { to: '/ai-insights',    icon: RiBrainLine,           label: 'AI Insights' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const initial = user?.username?.[0]?.toUpperCase() ?? '?'

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon"><RiBankLine /></div>
        <div className="sidebar-logo-text">Bank<span>Analyzer</span></div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Navigation</div>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <Icon />{label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-avatar">{initial}</div>
        <div className="sidebar-user-info">
          <div className="sidebar-user-name">{user?.username}</div>
          <div className="sidebar-user-email">{user?.email}</div>
        </div>
        <button className="logout-btn btn" title="Déconnexion" onClick={handleLogout}>
          <RiLogoutBoxLine style={{ fontSize: 18 }} />
        </button>
      </div>
    </aside>
  )
}
