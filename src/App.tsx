@ts-nocheck
import { useState } from 'react'
import Sidebar from './components/layout/Sidebar'
import CommunityPage from './pages/CommunityPage'
import DashboardPage from './pages/DashboardPage'

function App() {
  const [currentPage, setCurrentPage] = useState<'community' | 'dashboard'>('community')

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
      <main className="flex-1 ml-64">
        {currentPage === 'community' ? <CommunityPage /> : <DashboardPage />}
      </main>
    </div>
  )
}

export default App
