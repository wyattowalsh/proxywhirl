import { useNavigate, useParams } from "react-router-dom"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { PROTOCOLS, PROTOCOL_LABELS, type Protocol } from "@/types"

export function ProtocolTabs() {
  const navigate = useNavigate()
  const { protocol } = useParams<{ protocol?: string }>()
  const currentProtocol = (protocol as Protocol) || "http"

  return (
    <Tabs
      value={currentProtocol}
      onValueChange={(value) => navigate(`/proxies/${value}`)}
    >
      <TabsList className="grid w-full grid-cols-4">
        {PROTOCOLS.filter(p => p !== "https").map((p) => (
          <TabsTrigger key={p} value={p}>
            {PROTOCOL_LABELS[p]}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  )
}
