import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout/Layout'

import LoginPage           from './pages/LoginPage'
import RegisterPage        from './pages/RegisterPage'
import DashboardPage       from './pages/DashboardPage'
import UploadPage          from './pages/UploadPage'
import TransactionsPage    from './pages/TransactionsPage'
import AnomaliesPage       from './pages/AnomaliesPage'
import RecommendationsPage from './pages/RecommendationsPage'
import AIInsightsPage      from './pages/AIInsightsPage'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login"    element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={
        <ProtectedRoute>
          <Layout><DashboardPage /></Layout>
        </ProtectedRoute>
      }/>
      <Route path="/upload" element={
        <ProtectedRoute>
          <Layout><UploadPage /></Layout>
        </ProtectedRoute>
      }/>
      <Route path="/transactions" element={
        <ProtectedRoute>
          <Layout><TransactionsPage /></Layout>
        </ProtectedRoute>
      }/>
      <Route path="/anomalies" element={
        <ProtectedRoute>
          <Layout><AnomaliesPage /></Layout>
        </ProtectedRoute>
      }/>
      <Route path="/recommendations" element={
        <ProtectedRoute>
          <Layout><RecommendationsPage /></Layout>
        </ProtectedRoute>
      }/>
      <Route path="/ai-insights" element={
        <ProtectedRoute>
          <Layout><AIInsightsPage /></Layout>
        </ProtectedRoute>
      }/>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
