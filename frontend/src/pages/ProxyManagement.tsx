import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'
import { Progress } from '../components/ui/progress'
import { ProxyTable } from '../components/proxy/ProxyTable'
import { ProxyForm } from '../components/proxy/ProxyForm'
import { 
  ServerIcon,
  GlobeAltIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'

// Mock statistics
const proxyStats = {
  total: 12,
  active: 8,
  inactive: 2,
  validating: 1,
  failed: 1,
  avgResponseTime: 145,
  avgSuccessRate: 94.2,
  totalCountries: 5,
  totalUptime: 98.1
}

const StatCard: React.FC<{
  title: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  trend?: {
    value: number
    direction: 'up' | 'down'
  }
}> = ({ title, value, subtitle, icon, trend }) => (
  <Card>
    <CardContent className="flex items-center p-6">
      <div className="flex items-center space-x-4 flex-1">
        <div className="p-2 bg-primary/10 rounded-lg">
          {icon}
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <div className="flex items-center space-x-2">
            <h3 className="text-2xl font-bold">{value}</h3>
            {subtitle && (
              <span className="text-sm text-muted-foreground">{subtitle}</span>
            )}
          </div>
          {trend && (
            <p className={`text-xs ${trend.direction === 'up' ? 'text-green-600' : 'text-red-600'}`}>
              {trend.direction === 'up' ? '↗' : '↘'} {Math.abs(trend.value)}% from last week
            </p>
          )}
        </div>
      </div>
    </CardContent>
  </Card>
)

const StatusOverview: React.FC = () => (
  <Card className="col-span-full">
    <CardHeader>
      <CardTitle>Proxy Status Overview</CardTitle>
      <CardDescription>Real-time status distribution of your proxy pool</CardDescription>
    </CardHeader>
    <CardContent>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="flex items-center space-x-2">
          <CheckCircleIcon className="h-5 w-5 text-green-500" />
          <div>
            <p className="text-sm font-medium">Active</p>
            <p className="text-2xl font-bold text-green-600">{proxyStats.active}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <ClockIcon className="h-5 w-5 text-yellow-500" />
          <div>
            <p className="text-sm font-medium">Validating</p>
            <p className="text-2xl font-bold text-yellow-600">{proxyStats.validating}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <XCircleIcon className="h-5 w-5 text-gray-500" />
          <div>
            <p className="text-sm font-medium">Inactive</p>
            <p className="text-2xl font-bold text-gray-600">{proxyStats.inactive}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <XCircleIcon className="h-5 w-5 text-red-500" />
          <div>
            <p className="text-sm font-medium">Failed</p>
            <p className="text-2xl font-bold text-red-600">{proxyStats.failed}</p>
          </div>
        </div>
      </div>
      
      <div className="mt-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Overall Pool Health</span>
          <span className="text-sm text-muted-foreground">
            {proxyStats.active} of {proxyStats.total} proxies active
          </span>
        </div>
        <Progress 
          value={(proxyStats.active / proxyStats.total) * 100} 
          className="h-2"
        />
      </div>
    </CardContent>
  </Card>
)

const ProxyManagement: React.FC = () => {
  const handleAddProxy = (data: any) => {
    console.log('Adding proxy:', data)
    // Here you would typically call your API
  }

  const handleBulkValidation = () => {
    console.log('Starting bulk validation...')
    // Here you would trigger bulk validation
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Proxy Management</h1>
          <p className="text-muted-foreground">
            Monitor, validate, and manage your proxy pool
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={handleBulkValidation}>
            <ArrowPathIcon className="mr-2 h-4 w-4" />
            Validate All
          </Button>
          <ProxyForm onSubmit={handleAddProxy} />
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Proxies"
          value={proxyStats.total}
          icon={<ServerIcon className="h-5 w-5 text-primary" />}
          trend={{ value: 12, direction: 'up' }}
        />
        <StatCard
          title="Avg Response Time"
          value={proxyStats.avgResponseTime}
          subtitle="ms"
          icon={<ClockIcon className="h-5 w-5 text-primary" />}
          trend={{ value: 8, direction: 'down' }}
        />
        <StatCard
          title="Success Rate"
          value={`${proxyStats.avgSuccessRate}%`}
          icon={<CheckCircleIcon className="h-5 w-5 text-primary" />}
          trend={{ value: 2.1, direction: 'up' }}
        />
        <StatCard
          title="Countries"
          value={proxyStats.totalCountries}
          icon={<GlobeAltIcon className="h-5 w-5 text-primary" />}
        />
      </div>

      {/* Status Overview */}
      <StatusOverview />

      {/* Proxy Table */}
      <ProxyTable />
    </div>
  )
}

export default ProxyManagement
