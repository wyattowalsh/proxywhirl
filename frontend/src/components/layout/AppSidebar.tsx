import React from 'react'
import { useLocation, Link } from 'react-router-dom'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '../ui/sidebar'
import { Badge } from '../ui/badge'
import { Separator } from '../ui/separator'
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar'
import { 
  ChartBarIcon, 
  Cog6ToothIcon, 
  HomeIcon, 
  ServerIcon,
  ChartPieIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'

const navigation = [
  {
    name: 'Dashboard',
    href: '/',
    icon: HomeIcon,
    badge: null,
  },
  {
    name: 'Proxy List', 
    href: '/proxies',
    icon: ServerIcon,
    badge: '1,247',
  },
  {
    name: 'Analytics',
    href: '/analytics', 
    icon: ChartBarIcon,
    badge: null,
  },
  {
    name: 'Geographic',
    href: '/geographic',
    icon: ChartPieIcon,
    badge: '42',
  },
  {
    name: 'Validation',
    href: '/validation',
    icon: ClockIcon,
    badge: '12',
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Cog6ToothIcon,
    badge: null,
  },
]

const healthStats = [
  { label: 'Active Proxies', value: '1,247', status: 'success' },
  { label: 'Failed', value: '23', status: 'error' },
  { label: 'Validating', value: '12', status: 'warning' },
]

export const AppSidebar: React.FC = () => {
  const location = useLocation()

  return (
    <Sidebar className="border-r">
      <SidebarHeader className="border-b px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ServerIcon className="h-4 w-4" />
          </div>
          <div>
            <h1 className="font-semibold">ProxyWhirl</h1>
            <p className="text-xs text-muted-foreground">Command Center</p>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigation.map((item) => (
                <SidebarMenuItem key={item.name}>
                  <SidebarMenuButton asChild isActive={location.pathname === item.href}>
                    <Link to={item.href} className="flex items-center gap-3">
                      <item.icon className="h-4 w-4" />
                      <span>{item.name}</span>
                      {item.badge && (
                        <Badge variant="secondary" className="ml-auto">
                          {item.badge}
                        </Badge>
                      )}
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <Separator className="my-4" />

        <SidebarGroup>
          <SidebarGroupLabel>Health Status</SidebarGroupLabel>
          <SidebarGroupContent>
            <div className="space-y-3 px-3">
              {healthStats.map((stat) => (
                <div key={stat.label} className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">{stat.label}</span>
                  <Badge 
                    variant={stat.status === 'success' ? 'default' : stat.status === 'error' ? 'destructive' : 'secondary'}
                    className="text-xs"
                  >
                    {stat.value}
                  </Badge>
                </div>
              ))}
            </div>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t p-4">
        <div className="flex items-center gap-3">
          <Avatar className="h-8 w-8">
            <AvatarImage src="/placeholder-avatar.jpg" alt="User" />
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">Admin User</p>
            <p className="text-xs text-muted-foreground">admin@proxywhirl.com</p>
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
