import React from 'react'
import { SidebarProvider } from '../ui/sidebar'
import { AppSidebar } from './AppSidebar'
import { Header } from './Header'
import { MainContent } from './MainContent'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <SidebarProvider>
        <div className="flex h-screen w-full">
          <AppSidebar />
          <div className="flex flex-1 flex-col overflow-hidden">
            <Header />
            <MainContent>
              {children}
            </MainContent>
          </div>
        </div>
      </SidebarProvider>
    </div>
  )
}

export default Layout
