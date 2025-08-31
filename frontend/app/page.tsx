'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  BarChart3, 
  Users, 
  Phone, 
  FileText, 
  Settings, 
  LogOut,
  Plus,
  TrendingUp,
  Globe,
  Clock
} from 'lucide-react'
import { useQuery } from 'react-query'
import axios from 'axios'
import toast from 'react-hot-toast'

interface DashboardStats {
  totalSurveys: number
  activeSurveys: number
  totalContacts: number
  completedCalls: number
  responseRate: number
  recentActivity: Array<{
    id: string
    type: string
    message: string
    timestamp: string
  }>
}

export default function Dashboard() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<any>(null)

  // Mock data for demonstration
  const mockStats: DashboardStats = {
    totalSurveys: 12,
    activeSurveys: 5,
    totalContacts: 1250,
    completedCalls: 890,
    responseRate: 71.2,
    recentActivity: [
      {
        id: '1',
        type: 'survey',
        message: 'New survey "Customer Satisfaction 2024" created',
        timestamp: '2 hours ago'
      },
      {
        id: '2',
        type: 'call',
        message: 'Call completed with +91 98765 43210',
        timestamp: '3 hours ago'
      },
      {
        id: '3',
        type: 'upload',
        message: 'Contact list uploaded for Survey #8',
        timestamp: '5 hours ago'
      }
    ]
  }

  const { data: stats = mockStats, isLoading } = useQuery<DashboardStats>(
    'dashboard-stats',
    async () => {
      try {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/analytics/dashboard`)
        return response.data
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error)
        return mockStats
      }
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  )

  useEffect(() => {
    // Check authentication status
    const token = localStorage.getItem('access_token')
    if (token) {
      setIsAuthenticated(true)
      // Fetch user info
      fetchUserInfo()
    } else {
      router.push('/login')
    }
  }, [router])

  const fetchUserInfo = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUser(response.data)
    } catch (error) {
      console.error('Failed to fetch user info:', error)
      localStorage.removeItem('access_token')
      router.push('/login')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    setIsAuthenticated(false)
    router.push('/login')
    toast.success('Logged out successfully')
  }

  const navigationItems = [
    { name: 'Dashboard', icon: BarChart3, href: '/', current: true },
    { name: 'Surveys', icon: FileText, href: '/surveys', current: false },
    { name: 'Contacts', icon: Users, href: '/contacts', current: false },
    { name: 'Calls', icon: Phone, href: '/calls', current: false },
    { name: 'Analytics', icon: TrendingUp, href: '/analytics', current: false },
    { name: 'Settings', icon: Settings, href: '/settings', current: false },
  ]

  if (!isAuthenticated) {
    return <div>Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-center border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <Globe className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">AI Survey</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-4 py-4">
            {navigationItems.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                  item.current
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </a>
            ))}
          </nav>

          {/* User info */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                <span className="text-sm font-medium text-primary-700">
                  {user?.full_name?.charAt(0) || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.full_name || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user?.email || 'user@example.com'}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="pl-64">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-600">Welcome back! Here's what's happening with your surveys.</p>
              </div>
              <button className="btn-primary flex items-center space-x-2">
                <Plus className="h-4 w-4" />
                <span>New Survey</span>
              </button>
            </div>
          </div>
        </header>

        {/* Dashboard content */}
        <main className="p-6">
          {/* Stats cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <FileText className="h-8 w-8 text-primary-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Surveys</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalSurveys}</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <TrendingUp className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Active Surveys</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.activeSurveys}</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Users className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Contacts</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalContacts.toLocaleString()}</p>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Phone className="h-8 w-8 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Response Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.responseRate}%</p>
                </div>
              </div>
            </div>
          </div>

          {/* Recent activity and quick actions */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent activity */}
            <div className="lg:col-span-2">
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Recent Activity</h3>
                </div>
                <div className="space-y-4">
                  {stats.recentActivity.map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <div className="h-2 w-2 bg-primary-600 rounded-full mt-2"></div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900">{activity.message}</p>
                        <p className="text-xs text-gray-500 flex items-center mt-1">
                          <Clock className="h-3 w-3 mr-1" />
                          {activity.timestamp}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Quick actions */}
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Quick Actions</h3>
              </div>
              <div className="space-y-3">
                <button className="w-full btn-primary flex items-center justify-center space-x-2">
                  <Plus className="h-4 w-4" />
                  <span>Create Survey</span>
                </button>
                <button className="w-full btn-secondary flex items-center justify-center space-x-2">
                  <Users className="h-4 w-4" />
                  <span>Upload Contacts</span>
                </button>
                <button className="w-full btn-secondary flex items-center justify-center space-x-2">
                  <Phone className="h-4 w-4" />
                  <span>Schedule Calls</span>
                </button>
                <button className="w-full btn-secondary flex items-center justify-center space-x-2">
                  <BarChart3 className="h-4 w-4" />
                  <span>View Analytics</span>
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
