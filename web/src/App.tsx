import { createHashRouter, RouterProvider } from "react-router-dom"
import { Toaster } from "sonner"
import { Layout } from "@/components/layout/Layout"
import { Home } from "@/pages/Home"

const router = createHashRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
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
