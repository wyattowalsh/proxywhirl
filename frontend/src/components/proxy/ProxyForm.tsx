import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '../ui/form'
import { Input } from '../ui/input'
import { Button } from '../ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select'
import { Switch } from '../ui/switch'
import { Badge } from '../ui/badge'
import { Textarea } from '../ui/textarea'
import { PlusIcon } from '@heroicons/react/24/outline'

const proxyFormSchema = z.object({
  host: z.string().min(1, 'Host is required').refine(
    (value) => {
      // Basic IP address or hostname validation
      const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
      const hostnameRegex = /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/
      return ipRegex.test(value) || hostnameRegex.test(value)
    },
    'Must be a valid IP address or hostname'
  ),
  port: z.number().min(1, 'Port must be between 1 and 65535').max(65535, 'Port must be between 1 and 65535'),
  protocol: z.enum(['HTTP', 'HTTPS', 'SOCKS4', 'SOCKS5']),
  username: z.string().optional(),
  password: z.string().optional(),
  country: z.string().min(1, 'Country is required'),
  city: z.string().min(1, 'City is required'),
  enabled: z.boolean().default(true),
  description: z.string().optional(),
  tags: z.string().optional().transform((val) => 
    val ? val.split(',').map(tag => tag.trim()).filter(Boolean) : []
  ),
})

type ProxyFormData = z.infer<typeof proxyFormSchema>

interface ProxyFormProps {
  onSubmit: (data: ProxyFormData) => void
  initialData?: Partial<ProxyFormData>
  isLoading?: boolean
  trigger?: React.ReactNode
}

export const ProxyForm: React.FC<ProxyFormProps> = ({
  onSubmit,
  initialData,
  isLoading = false,
  trigger
}) => {
  const [open, setOpen] = React.useState(false)

  const form = useForm<ProxyFormData>({
    resolver: zodResolver(proxyFormSchema),
    defaultValues: {
      host: initialData?.host ?? '',
      port: initialData?.port ?? 8080,
      protocol: initialData?.protocol ?? 'HTTP',
      username: initialData?.username ?? '',
      password: initialData?.password ?? '',
      country: initialData?.country ?? '',
      city: initialData?.city ?? '',
      enabled: initialData?.enabled ?? true,
      description: initialData?.description ?? '',
      tags: initialData?.tags ?? [],
    },
  })

  const handleSubmit = (data: ProxyFormData) => {
    onSubmit(data)
    setOpen(false)
    form.reset()
  }

  const defaultTrigger = (
    <Button>
      <PlusIcon className="mr-2 h-4 w-4" />
      Add Proxy
    </Button>
  )

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || defaultTrigger}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {initialData ? 'Edit Proxy' : 'Add New Proxy'}
          </DialogTitle>
          <DialogDescription>
            {initialData 
              ? 'Update the proxy configuration below.'
              : 'Add a new proxy to your pool. All fields marked with * are required.'
            }
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="host"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Host *</FormLabel>
                    <FormControl>
                      <Input placeholder="192.168.1.100 or proxy.example.com" {...field} />
                    </FormControl>
                    <FormDescription>
                      IP address or hostname of the proxy server
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="port"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Port *</FormLabel>
                    <FormControl>
                      <Input 
                        type="number"
                        placeholder="8080"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                      />
                    </FormControl>
                    <FormDescription>
                      Port number (1-65535)
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="protocol"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Protocol *</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select protocol" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="HTTP">HTTP</SelectItem>
                      <SelectItem value="HTTPS">HTTPS</SelectItem>
                      <SelectItem value="SOCKS4">SOCKS4</SelectItem>
                      <SelectItem value="SOCKS5">SOCKS5</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormDescription>
                    Protocol type for the proxy connection
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Username</FormLabel>
                    <FormControl>
                      <Input placeholder="username" {...field} />
                    </FormControl>
                    <FormDescription>
                      Optional authentication username
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="password" {...field} />
                    </FormControl>
                    <FormDescription>
                      Optional authentication password
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="country"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Country *</FormLabel>
                    <FormControl>
                      <Input placeholder="United States" {...field} />
                    </FormControl>
                    <FormDescription>
                      Proxy server location country
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="city"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>City *</FormLabel>
                    <FormControl>
                      <Input placeholder="New York" {...field} />
                    </FormControl>
                    <FormDescription>
                      Proxy server location city
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="enabled"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                  <div className="space-y-0.5">
                    <FormLabel className="text-base">
                      Enable Proxy
                    </FormLabel>
                    <FormDescription>
                      Whether this proxy should be active in the pool
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Optional description for this proxy..."
                      className="resize-none"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Optional notes about this proxy
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="tags"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tags</FormLabel>
                  <FormControl>
                    <Input 
                      placeholder="residential, fast, premium (comma-separated)"
                      {...field}
                      value={Array.isArray(field.value) ? field.value.join(', ') : field.value}
                    />
                  </FormControl>
                  <FormDescription>
                    Comma-separated tags for organizing proxies
                  </FormDescription>
                  <FormMessage />
                  {field.value && Array.isArray(field.value) && field.value.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {field.value.map((tag, index) => (
                        <Badge key={index} variant="outline">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Saving...' : initialData ? 'Update Proxy' : 'Add Proxy'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
