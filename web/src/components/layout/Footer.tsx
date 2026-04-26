export function Footer() {
  return (
    <footer className="border-t py-6 md:py-0">
      <div className="container flex flex-col items-center justify-between gap-4 md:h-14 md:flex-row">
        <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
          Built with{" "}
          <a
            href="https://github.com/wyattowalsh/proxywhirl"
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium underline underline-offset-4"
          >
            ProxyWhirl
          </a>
          . Proxy lists updated every 6 hours.
        </p>
        <p className="text-center text-sm text-muted-foreground md:text-right">
          Free and open source.
        </p>
      </div>
    </footer>
  )
}
