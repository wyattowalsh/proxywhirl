import { Download } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useDownload } from "@/hooks/useProxies"
import type { Protocol } from "@/types"
import { formatBytes } from "@/lib/utils"

interface DownloadButtonProps {
  protocol: Protocol
  fileSize?: number
}

export function DownloadButton({ protocol, fileSize }: DownloadButtonProps) {
  const { download } = useDownload()

  return (
    <Button onClick={() => download(protocol)} className="gap-2">
      <Download className="h-4 w-4" />
      Download {protocol.toUpperCase()}
      {fileSize && (
        <span className="text-xs opacity-70">({formatBytes(fileSize)})</span>
      )}
    </Button>
  )
}

export function DownloadAllButton({ fileSize }: { fileSize?: number }) {
  const { download } = useDownload()

  return (
    <Button variant="outline" onClick={() => download("all")} className="gap-2">
      <Download className="h-4 w-4" />
      Download All
      {fileSize && (
        <span className="text-xs opacity-70">({formatBytes(fileSize)})</span>
      )}
    </Button>
  )
}
