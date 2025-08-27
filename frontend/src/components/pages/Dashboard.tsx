import React from 'react';
import { useProxyManagement } from '../../hooks/useProxyManagement';

const MetricCard: React.FC<{
  title: string;
  value: string | number;
  change?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
}> = ({ title, value, change, icon, trend = 'neutral' }) => (
  <div className="metric-card group hover:shadow-md transition-all duration-300">
    <div className="flex items-center justify-between">
      <div className="text-muted-foreground group-hover:text-foreground transition-colors">
        {icon}
      </div>
      {change && (
        <span className={`text-sm px-2 py-1 rounded-full ${
          trend === 'up' ? 'text-success bg-success/10' :
          trend === 'down' ? 'text-error bg-error/10' :
          'text-muted-foreground bg-muted'
        }`}>
          {change}
        </span>
      )}
    </div>
    <div className="mt-3">
      <h3 className="text-2xl font-bold text-foreground">{value}</h3>
      <p className="text-sm text-muted-foreground mt-1">{title}</p>
    </div>
  </div>
);

const QuickActionButton: React.FC<{
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}> = ({ label, icon, onClick, variant = 'secondary' }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-3 p-4 rounded-lg transition-all duration-200 ${
      variant === 'primary' 
        ? 'bg-primary text-primary-foreground hover:bg-primary/90' 
        : 'bg-card border border-border hover:bg-accent hover:text-accent-foreground'
    } interactive-subtle`}
  >
    {icon}
    <span className="font-medium">{label}</span>
  </button>
);

const RecentActivityItem: React.FC<{
  action: string;
  target: string;
  time: string;
  status: 'success' | 'warning' | 'error';
}> = ({ action, target, time, status }) => (
  <div className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors">
    <div className="flex items-center gap-3">
      <div className={`status-dot ${status}`}></div>
      <div>
        <p className="text-sm font-medium text-foreground">{action}</p>
        <p className="text-xs text-muted-foreground">{target}</p>
      </div>
    </div>
    <span className="text-xs text-muted-foreground">{time}</span>
  </div>
);

export const Dashboard: React.FC = () => {
  const { useProxies } = useProxyManagement();
  const { data, isLoading } = useProxies();

  // Mock data for demonstration
  const mockMetrics = {
    activeProxies: 247,
    totalProxies: 500,
    successRate: '94.2%',
    avgResponseTime: '125ms'
  };

  const mockActivities = [
    { action: 'Proxy validated', target: '192.168.1.100:8080', time: '2 min ago', status: 'success' as const },
    { action: 'Validation failed', target: '10.0.0.50:3128', time: '5 min ago', status: 'error' as const },
    { action: 'New proxy added', target: '172.16.0.10:8080', time: '12 min ago', status: 'success' as const },
    { action: 'Proxy timeout', target: '203.0.113.20:8080', time: '18 min ago', status: 'warning' as const },
  ];

  if (isLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="skeleton h-8 w-48"></div>
        <div className="grid-analytics">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton h-32"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Monitor your proxy infrastructure and performance metrics
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <QuickActionButton
            label="Validate All"
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
            onClick={() => console.log('Validate all proxies')}
            variant="primary"
          />
          <QuickActionButton
            label="Add Proxy"
            icon={
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            }
            onClick={() => console.log('Add new proxy')}
          />
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid-analytics">
        <MetricCard
          title="Active Proxies"
          value={mockMetrics.activeProxies.toLocaleString()}
          change="+12"
          trend="up"
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" />
            </svg>
          }
        />
        <MetricCard
          title="Total Proxies"
          value={mockMetrics.totalProxies.toLocaleString()}
          change="+25"
          trend="up"
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          }
        />
        <MetricCard
          title="Success Rate"
          value={mockMetrics.successRate}
          change="+2.1%"
          trend="up"
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          }
        />
        <MetricCard
          title="Avg Response Time"
          value={mockMetrics.avgResponseTime}
          change="-15ms"
          trend="up"
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />
      </div>

      {/* Dashboard Grid */}
      <div className="grid-dashboard">
        {/* Recent Activity */}
        <div className="lg:col-span-8">
          <div className="card-enhanced">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-foreground">Recent Activity</h2>
              <button className="text-sm text-primary hover:text-primary/80 transition-colors">
                View all
              </button>
            </div>
            <div className="space-y-2">
              {mockActivities.map((activity, index) => (
                <RecentActivityItem key={index} {...activity} />
              ))}
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="lg:col-span-4">
          <div className="card-enhanced">
            <h2 className="text-xl font-semibold text-foreground mb-6">Quick Stats</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Uptime</span>
                <span className="font-semibold text-success">99.9%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Failed Today</span>
                <span className="font-semibold text-error">3</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Validations</span>
                <span className="font-semibold text-warning">1.2K</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Countries</span>
                <span className="font-semibold text-info">24</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
