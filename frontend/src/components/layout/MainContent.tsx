import React from 'react';

interface MainContentProps {
  children: React.ReactNode;
}

export const MainContent: React.FC<MainContentProps> = ({ children }) => {
  return (
    <main className="flex-1 overflow-y-auto bg-background">
      {/* Main content area with proper spacing for desktop sidebar */}
      <div className="lg:pl-64">
        <div className="container-responsive py-6 min-h-full">
          {children}
        </div>
      </div>
    </main>
  );
};
