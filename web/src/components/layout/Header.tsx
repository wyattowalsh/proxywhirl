import { Link, useLocation } from "react-router-dom"
import { Github, Moon, Sun, Wifi, BookOpen, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { useEffect, useState } from "react"

export function Header() {
  const location = useLocation()
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== "undefined") {
      return document.documentElement.classList.contains("dark")
    }
    return true
  })

  useEffect(() => {
    // Check system preference on mount
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
    const stored = localStorage.getItem("theme")
    const shouldBeDark = stored ? stored === "dark" : prefersDark
    setIsDark(shouldBeDark)
    document.documentElement.classList.toggle("dark", shouldBeDark)
  }, [])

  const toggleTheme = () => {
    const newIsDark = !isDark
    setIsDark(newIsDark)
    document.documentElement.classList.toggle("dark", newIsDark)
    localStorage.setItem("theme", newIsDark ? "dark" : "light")
  }

  const navItems: { path: string; label: string }[] = []

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <Link to="/" className="mr-6 flex items-center space-x-2">
          <Wifi className="h-6 w-6 text-primary" />
          <span className="font-bold">ProxyWhirl</span>
        </Link>

        <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "transition-colors hover:text-foreground/80",
                location.pathname === item.path
                  ? "text-foreground"
                  : "text-foreground/60"
              )}
            >
              {item.label}
            </Link>
          ))}
          <a
            href={`${import.meta.env.BASE_URL}docs/`}
            className="flex items-center gap-1 transition-colors hover:text-foreground/80 text-foreground/60"
          >
            <BookOpen className="h-4 w-4" />
            Docs
          </a>
        </nav>

        <div className="flex flex-1 items-center justify-end space-x-2">
          <Button variant="ghost" size="icon" onClick={toggleTheme}>
            {isDark ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
            <span className="sr-only">Toggle theme</span>
          </Button>
          <Button variant="ghost" size="icon" asChild className="hidden md:flex">
            <a
              href="https://github.com/wyattowalsh/proxywhirl"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github className="h-5 w-5" />
              <span className="sr-only">GitHub</span>
            </a>
          </Button>
          
          {/* Mobile Menu */}
          <div className="md:hidden">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <Menu className="h-5 w-5" />
                  <span className="sr-only">Toggle menu</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem asChild>
                  <a href={`${import.meta.env.BASE_URL}docs/`} className="cursor-pointer">
                    <BookOpen className="mr-2 h-4 w-4" />
                    Docs
                  </a>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <a
                    href="https://github.com/wyattowalsh/proxywhirl"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="cursor-pointer"
                  >
                    <Github className="mr-2 h-4 w-4" />
                    GitHub
                  </a>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  )
}
