const TITLES = {
  '/':               { title: 'Dashboard',        subtitle: 'Vue d\'ensemble de vos finances' },
  '/upload':         { title: 'Import CSV',        subtitle: 'Importer vos transactions bancaires' },
  '/transactions':   { title: 'Transactions',      subtitle: 'Historique de toutes vos opérations' },
  '/anomalies':      { title: 'Anomalies',         subtitle: 'Transactions inhabituelles détectées' },
  '/recommendations':{ title: 'Recommandations',   subtitle: 'Conseils budgétaires intelligents' },
}

export default function Header({ pathname }) {
  const { title, subtitle } = TITLES[pathname] ?? { title: 'BankAnalyzer', subtitle: '' }
  return (
    <header className="header">
      <div>
        <div className="header-title">{title}</div>
        {subtitle && <div className="header-subtitle">{subtitle}</div>}
      </div>
    </header>
  )
}
