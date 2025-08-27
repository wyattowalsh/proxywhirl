import React, { useState } from 'react'
import {
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
} from '@tanstack/react-table'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Badge } from '../ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Progress } from '../ui/progress'
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger,
  DropdownMenuSeparator
} from '../ui/dropdown-menu'
import { 
  ChevronDownIcon, 
  ChevronUpIcon, 
  EllipsisHorizontalIcon,
  PlayIcon,
  PauseIcon,
  TrashIcon,
  PencilIcon
} from '@heroicons/react/24/outline'

// Mock data types
interface Proxy {
  id: string
  host: string
  port: number
  protocol: 'HTTP' | 'HTTPS' | 'SOCKS4' | 'SOCKS5'
  country: string
  city: string
  status: 'active' | 'inactive' | 'validating' | 'failed'
  responseTime: number | null
  successRate: number
  lastChecked: Date
  uptime: number
}

// Mock data
const mockProxies: Proxy[] = [
  {
    id: '1',
    host: '192.168.1.100',
    port: 8080,
    protocol: 'HTTP',
    country: 'United States',
    city: 'New York',
    status: 'active',
    responseTime: 120,
    successRate: 98.5,
    lastChecked: new Date(),
    uptime: 99.2,
  },
  {
    id: '2',
    host: '10.0.0.50',
    port: 3128,
    protocol: 'HTTPS',
    country: 'Germany',
    city: 'Berlin',
    status: 'validating',
    responseTime: 85,
    successRate: 95.2,
    lastChecked: new Date(Date.now() - 300000),
    uptime: 97.8,
  },
  {
    id: '3',
    host: '172.16.0.25',
    port: 1080,
    protocol: 'SOCKS5',
    country: 'Japan',
    city: 'Tokyo',
    status: 'failed',
    responseTime: null,
    successRate: 0,
    lastChecked: new Date(Date.now() - 600000),
    uptime: 0,
  },
]

const StatusBadge: React.FC<{ status: Proxy['status'] }> = ({ status }) => {
  const variants = {
    active: { variant: 'default' as const, color: 'bg-green-500', text: 'Active' },
    inactive: { variant: 'secondary' as const, color: 'bg-gray-500', text: 'Inactive' },
    validating: { variant: 'outline' as const, color: 'bg-yellow-500', text: 'Validating' },
    failed: { variant: 'destructive' as const, color: 'bg-red-500', text: 'Failed' },
  }

  const config = variants[status]
  
  return (
    <Badge variant={config.variant} className="gap-1">
      <div className={`h-2 w-2 rounded-full ${config.color}`} />
      {config.text}
    </Badge>
  )
}

export const ProxyTable: React.FC = () => {
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState('')

  const columns: ColumnDef<Proxy>[] = [
    {
      accessorKey: 'host',
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="h-auto p-0 hover:bg-transparent"
          >
            Host
            {column.getIsSorted() === 'asc' ? (
              <ChevronUpIcon className="ml-2 h-4 w-4" />
            ) : column.getIsSorted() === 'desc' ? (
              <ChevronDownIcon className="ml-2 h-4 w-4" />
            ) : null}
          </Button>
        )
      },
      cell: ({ row }) => (
        <div className="font-mono">
          <div className="font-medium">{row.getValue('host')}</div>
          <div className="text-sm text-muted-foreground">:{row.original.port}</div>
        </div>
      ),
    },
    {
      accessorKey: 'protocol',
      header: 'Protocol',
      cell: ({ row }) => (
        <Badge variant="outline">{row.getValue('protocol')}</Badge>
      ),
    },
    {
      accessorKey: 'country',
      header: 'Location',
      cell: ({ row }) => (
        <div>
          <div className="font-medium">{row.original.country}</div>
          <div className="text-sm text-muted-foreground">{row.original.city}</div>
        </div>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => <StatusBadge status={row.getValue('status')} />,
    },
    {
      accessorKey: 'responseTime',
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
            className="h-auto p-0 hover:bg-transparent"
          >
            Response Time
            {column.getIsSorted() === 'asc' ? (
              <ChevronUpIcon className="ml-2 h-4 w-4" />
            ) : column.getIsSorted() === 'desc' ? (
              <ChevronDownIcon className="ml-2 h-4 w-4" />
            ) : null}
          </Button>
        )
      },
      cell: ({ row }) => {
        const responseTime = row.getValue('responseTime') as number | null
        return responseTime ? `${responseTime}ms` : 'N/A'
      },
    },
    {
      accessorKey: 'successRate',
      header: 'Success Rate',
      cell: ({ row }) => {
        const rate = row.getValue('successRate') as number
        return (
          <div className="flex items-center gap-2">
            <Progress value={rate} className="w-16" />
            <span className="text-sm font-medium w-12">{rate.toFixed(1)}%</span>
          </div>
        )
      },
    },
    {
      accessorKey: 'lastChecked',
      header: 'Last Checked',
      cell: ({ row }) => {
        const date = row.getValue('lastChecked') as Date
        return (
          <div className="text-sm">
            {date.toLocaleDateString()}
            <br />
            <span className="text-muted-foreground">
              {date.toLocaleTimeString()}
            </span>
          </div>
        )
      },
    },
    {
      id: 'actions',
      cell: ({ row }) => {
        const proxy = row.original

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <EllipsisHorizontalIcon className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>
                <PlayIcon className="mr-2 h-4 w-4" />
                Test Proxy
              </DropdownMenuItem>
              <DropdownMenuItem>
                <PencilIcon className="mr-2 h-4 w-4" />
                Edit
              </DropdownMenuItem>
              {proxy.status === 'active' ? (
                <DropdownMenuItem>
                  <PauseIcon className="mr-2 h-4 w-4" />
                  Disable
                </DropdownMenuItem>
              ) : (
                <DropdownMenuItem>
                  <PlayIcon className="mr-2 h-4 w-4" />
                  Enable
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive">
                <TrashIcon className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  const table = useReactTable({
    data: mockProxies,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    state: {
      sorting,
      columnFilters,
      globalFilter,
    },
  })

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Proxy Management</CardTitle>
          <CardDescription>
            Manage and monitor your proxy pool with real-time status updates
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center py-4">
            <Input
              placeholder="Search proxies..."
              value={globalFilter ?? ''}
              onChange={(event) => setGlobalFilter(event.target.value)}
              className="max-w-sm"
            />
          </div>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    {headerGroup.headers.map((header) => {
                      return (
                        <TableHead key={header.id}>
                          {header.isPlaceholder
                            ? null
                            : flexRender(
                                header.column.columnDef.header,
                                header.getContext()
                              )}
                        </TableHead>
                      )
                    })}
                  </TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {table.getRowModel().rows?.length ? (
                  table.getRowModel().rows.map((row) => (
                    <TableRow
                      key={row.id}
                      data-state={row.getIsSelected() && 'selected'}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <TableCell key={cell.id}>
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={columns.length} className="h-24 text-center">
                      No results.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
          <div className="flex items-center justify-end space-x-2 py-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              Next
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
