import React from 'react';

export const ProxyList: React.FC = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Proxy List</h1>
          <p className="text-muted-foreground mt-1">
            Manage and monitor all your proxy servers
          </p>
        </div>
        <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
          Add New Proxy
        </button>
      </div>

      <div className="card-enhanced">
        <div className="flex items-center justify-center h-64">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-muted flex items-center justify-center">
              <svg className="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-medium text-foreground">Proxy Management Interface</h3>
              <p className="text-muted-foreground">
                Advanced proxy list with TanStack Table coming soon
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
