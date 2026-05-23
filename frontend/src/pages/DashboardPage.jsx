import { useNavigate } from 'react-router-dom'
import {
  RiMoneyDollarCircleLine, RiArrowDownCircleLine,
  RiWalletLine, RiExchangeLine, RiUploadCloud2Line,
} from 'react-icons/ri'

import { getKPI, getSpendingByCategory, getMonthlyEvolution, getTopMerchants } from '../api/analytics'
import { useApi } from '../hooks/useApi'
import KPICard from '../components/ui/KPICard'
import Spinner from '../components/ui/Spinner'
import Alert from '../components/ui/Alert'
import SpendingPieChart from '../components/charts/SpendingPieChart'
import MonthlyLineChart from '../components/charts/MonthlyLineChart'
import TopMerchantsBarChart from '../components/charts/TopMerchantsBarChart'
import { formatCurrency, formatNumber } from '../utils/formatters'

export default function DashboardPage() {
  const navigate = useNavigate()
  const kpi      = useApi(getKPI)
  const spending = useApi(getSpendingByCategory)
  const monthly  = useApi(getMonthlyEvolution)
  const merchants= useApi(getTopMerchants)

  const noData = !kpi.loading && kpi.data?.transaction_count === 0

  if (kpi.loading) return <Spinner />

  if (noData) return (
    <div className="empty-state" style={{ marginTop: 60 }}>
      <div className="empty-icon">📊</div>
      <div className="empty-title">Aucune transaction</div>
      <div className="empty-text">Importez un fichier CSV pour commencer votre analyse.</div>
      <div className="empty-action">
        <button className="btn btn-primary" onClick={() => navigate('/upload')}>
          <RiUploadCloud2Line /> Importer un fichier CSV
        </button>
      </div>
    </div>
  )

  return (
    <>
      {kpi.error && <Alert type="error" message={kpi.error} />}

      {/* KPIs */}
      <div className="kpi-grid">
        <KPICard icon={RiMoneyDollarCircleLine} color="green" label="Total crédits"
          value={kpi.data ? formatCurrency(kpi.data.total_credit) : '—'}
          sub={`${formatNumber(kpi.data?.credit_count)} opérations`} />
        <KPICard icon={RiArrowDownCircleLine} color="red" label="Total débits"
          value={kpi.data ? formatCurrency(kpi.data.total_debit) : '—'}
          sub={`${formatNumber(kpi.data?.debit_count)} opérations`} />
        <KPICard icon={RiWalletLine} color={kpi.data?.net_balance >= 0 ? 'green' : 'red'} label="Solde net"
          value={kpi.data ? formatCurrency(kpi.data.net_balance) : '—'}
          sub="Crédits − Débits" />
        <KPICard icon={RiExchangeLine} color="blue" label="Total transactions"
          value={kpi.data ? formatNumber(kpi.data.transaction_count) : '—'}
          sub="Toutes opérations" />
      </div>

      {/* Pie + Line */}
      <div className="charts-grid">
        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Dépenses par catégorie</div>
              <div className="card-subtitle">Répartition des débits</div>
            </div>
          </div>
          <div className="card-body">
            {spending.loading ? <Spinner /> : <SpendingPieChart data={spending.data} />}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">Évolution mensuelle</div>
              <div className="card-subtitle">Crédits vs Débits par mois</div>
            </div>
          </div>
          <div className="card-body">
            {monthly.loading ? <Spinner /> : <MonthlyLineChart data={monthly.data} />}
          </div>
        </div>
      </div>

      {/* Top merchants */}
      <div className="card chart-full">
        <div className="card-header">
          <div>
            <div className="card-title">Top 10 marchands</div>
            <div className="card-subtitle">Par montant total dépensé</div>
          </div>
        </div>
        <div className="card-body">
          {merchants.loading ? <Spinner /> : <TopMerchantsBarChart data={merchants.data} />}
        </div>
      </div>
    </>
  )
}
