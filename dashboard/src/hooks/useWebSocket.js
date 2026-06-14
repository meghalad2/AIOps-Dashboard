import { useEffect, useRef, useState, useCallback } from 'react'

export function useWebSocket(url, onMessage) {
  const ws = useRef(null)
  const [connected, setConnected] = useState(false)

  const connect = useCallback(() => {
    const socket = new WebSocket(url)

    socket.onopen = () => setConnected(true)
    socket.onclose = () => {
      setConnected(false)
      // Auto-reconnect after 3 seconds
      setTimeout(connect, 3000)
    }
    socket.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.type !== 'ping') onMessage(data)
      } catch (_) {}
    }

    ws.current = socket
  }, [url, onMessage])

  useEffect(() => {
    connect()
    return () => ws.current?.close()
  }, [connect])

  return connected
}
