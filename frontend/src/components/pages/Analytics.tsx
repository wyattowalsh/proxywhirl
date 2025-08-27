import React from 'react';

export const Analytics: React.FC = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
          <p className="text-muted-foreground mt-1">
            Performance insights and geographic distribution
          </p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-card border border-border rounded-lg hover:bg-accent transition-colors">
            Last 24h
          </button>
          <button className="px-4 py-2 bg-card border border-border rounded-lg hover:bg-accent transition-colors">
            Export Report
          </button>
        </div>
      </div>

      <div className="grid-dashboard">
        <div className="lg:col-span-6">
          <div className="card-enhanced">
            <h2 className="text-xl font-semibold text-foreground mb-4">Geographic Distribution</h2>
            <div className="chart-container bg-muted/30 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <svg className="w-16 h-16 mx-auto mb-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-muted-foreground">Interactive world map coming soon</p>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-6">
          <div className="card-enhanced">
            <h2 className="text-xl font-semibold text-foreground mb-4">Performance Trends</h2>
            <div className="chart-container bg-muted/30 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <svg className="w-16 h-16 mx-auto mb-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p className="text-muted-foreground">Recharts integration coming soon</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
