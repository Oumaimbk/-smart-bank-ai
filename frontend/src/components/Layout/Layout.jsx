import { useLocation } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

export default function Layout({ children }) {
  const { pathname } = useLocation()
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <Header pathname={pathname} />
        <main className="page-content">{children}</main>
      </div>
    </div>
  )
}
