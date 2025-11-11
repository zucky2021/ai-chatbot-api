import { useEffect, useRef, useState, useCallback } from 'react'

export interface WebSocketMessage {
  type: 'connected' | 'processing' | 'chunk' | 'done' | 'saved' | 'error' | 'pong'
  content?: string
  message?: string
  session_id?: string
  conversation_id?: number
}

export interface UseWebSocketOptions {
  sessionId: string
  userId?: string
  apiUrl?: string
  onMessage?: (message: WebSocketMessage) => void
  onError?: (error: Error) => void
  onOpen?: () => void
  onClose?: () => void
  autoReconnect?: boolean
  reconnectInterval?: number
}

export interface UseWebSocketReturn {
  isConnected: boolean
  currentResponse: string
  sendMessage: (message: string, metadata?: Record<string, unknown>) => void
  sendPing: () => void
  disconnect: () => void
  error: Error | null
}

export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    sessionId,
    userId = 'default_user',
    apiUrl = 'http://localhost:8000',
    onMessage,
    onError,
    onOpen,
    onClose,
    autoReconnect = true,
    reconnectInterval = 3000,
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [currentResponse, setCurrentResponse] = useState('')
  const [error, setError] = useState<Error | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const pingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const connect = useCallback(() => {
    // sessionIdが空の場合は接続しない
    if (!sessionId) {
      return
    }

    // 既存の接続がある場合は閉じる
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    try {
      const wsUrl = `${apiUrl.replace('http', 'ws')}/api/chat/ws?session_id=${sessionId}&user_id=${userId}`
      const ws = new WebSocket(wsUrl)

      let heartbeat: ReturnType<typeof setInterval> | null = null

      ws.onopen = () => {
        console.log('WebSocket接続が確立されました')
        setIsConnected(true)
        setError(null)
        onOpen?.()

        // ハートビート（30秒ごと）
        heartbeat = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }))
          }
        }, 30000)
        pingIntervalRef.current = heartbeat
      }

      ws.onmessage = event => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data)

          switch (data.type) {
            case 'connected':
              console.log('接続確立:', data.message)
              break

            case 'processing':
              console.log('処理開始:', data.message)
              setCurrentResponse('') // 新しい回答を開始
              break

            case 'chunk':
              if (data.content) {
                setCurrentResponse(prev => prev + data.content)
              }
              break

            case 'done':
              console.log('完了:', data.message)
              break

            case 'saved':
              console.log('保存完了:', data.conversation_id)
              break

            case 'error': {
              console.error('エラー:', data.message)
              const error = new Error(data.message || 'Unknown error')
              setError(error)
              onError?.(error)
              break
            }

            case 'pong':
              // ハートビート応答
              break

            default:
              console.warn('不明なメッセージタイプ:', data)
          }

          onMessage?.(data)
        } catch (err) {
          console.error('メッセージ解析エラー:', err)
          const error = new Error('メッセージの解析に失敗しました')
          setError(error)
          onError?.(error)
        }
      }

      ws.onerror = event => {
        console.error('WebSocketエラー:', event)
      }

      ws.onclose = event => {
        // ハートビートを停止（このインスタンスのものだけ）
        if (heartbeat) {
          clearInterval(heartbeat)
          if (pingIntervalRef.current === heartbeat) {
            pingIntervalRef.current = null
          }
          heartbeat = null
        }

        // 旧WebSocketのoncloseが後から発火した場合、最新接続を切断扱いにしない
        if (wsRef.current && wsRef.current !== ws) {
          return
        }

        // 正常な切断（1000, 1001）の場合はログを出力しない
        if (event.code !== 1000 && event.code !== 1001) {
          console.log('WebSocket接続が閉じられました', event.code, event.reason)
        }

        setIsConnected(false)

        // コード1005（No Status Received）は接続が確立されなかったことを示す
        // この場合はエラーを設定しない（接続確立前の切断のため）
        if (event.code !== 1000 && event.code !== 1001 && event.code !== 1005) {
          const error = new Error(`WebSocket接続が切断されました (コード: ${event.code})`)
          setError(error)
          onError?.(error)
        } else if (event.code === 1005) {
          // コード1005の場合は、接続が確立されなかったことを示す
          console.warn('WebSocket接続が確立されませんでした (コード: 1005)')
        }

        if (wsRef.current === ws) {
          wsRef.current = null
        }

        onClose?.()

        // 自動再接続は無効化（エラーを防ぐため）
        // 自動再接続が必要な場合は、手動で再接続する
      }

      wsRef.current = ws
    } catch (err) {
      console.error('WebSocket接続エラー:', err)
      const error = err instanceof Error ? err : new Error('WebSocket接続に失敗しました')
      setError(error)
      onError?.(error)
    }
  }, [
    sessionId,
    userId,
    apiUrl,
    onMessage,
    onError,
    onOpen,
    onClose,
    autoReconnect,
    reconnectInterval,
  ])

  const sendMessage = useCallback(
    (message: string, metadata?: Record<string, unknown>) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(
          JSON.stringify({
            type: 'message',
            message: message.trim(),
            metadata: metadata || {},
          })
        )
      } else {
        const error = new Error('WebSocket接続が確立されていません')
        setError(error)
        onError?.(error)
      }
    },
    [onError]
  )

  const sendPing = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'ping' }))
    }
  }, [])

  const disconnect = useCallback(() => {
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current)
      pingIntervalRef.current = null
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    setIsConnected(false)
  }, [])

  useEffect(() => {
    // sessionIdが設定されている場合のみ接続
    if (!sessionId) {
      return
    }

    // セッションが確実に作成されるまで待機してから接続
    const timer = setTimeout(() => {
      connect()
    }, 1000) // 1秒待機

    return () => {
      clearTimeout(timer)
      disconnect()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]) // connectとdisconnectは依存配列から除外（無限ループを防ぐため）

  return {
    isConnected,
    currentResponse,
    sendMessage,
    sendPing,
    disconnect,
    error,
  }
}
