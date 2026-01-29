import { lazy, Suspense } from "react"
import { createHashRouter, RouterProvider } from "react-router-dom"
import { Toaster } from "sonner"
import { Layout } from "@/components/layout/Layout"
import { Home } from "@/pages/Home"
import { Skeleton } from "@/components/ui/skeleton"

// Lazy-load the Analytics page
const AnalyticsPage = lazy(() =>
  import("@/pages/AnalyticsPage").then((m) => ({ default: m.AnalyticsPage }))
)

function AnalyticsPageSkeleton() {
  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-10 rounded" />
        <div>
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-48 mt-2" />
        </div>
      </div>
      <div className="grid gap-6 md:grid-cols-3">
        <Skeleton className="h-[300px]" />
        <Skeleton className="h-[300px]" />
        <Skeleton className="h-[300px]" />
      </div>
      <Skeleton className="h-[500px]" />
    </div>
  )
}

const router = createHashRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      {
        path: "analytics",
        element: (
          <Suspense fallback={<AnalyticsPageSkeleton />}>
            <AnalyticsPage />
          </Suspense>
        ),
      },
    ],
  },
])

export default function App() {
  return (
    <>
      <RouterProvider router={router} />
      <Toaster
        position="bottom-right"
        toastOptions={{
          className: "border bg-background text-foreground",
        }}
      />
    </>
  )
}
