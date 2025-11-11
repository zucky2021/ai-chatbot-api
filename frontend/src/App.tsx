import { useState, useEffect } from 'react'
import { ChatInterface } from './components/ChatInterface'
import './App.css'

function App() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    // セッションを作成
    const createSession = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/chat/sessions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            metadata: { language: 'ja' },
          }),
        })

        if (!response.ok) {
          throw new Error(`セッション作成に失敗しました: ${response.statusText}`)
        }

        const data = await response.json()
        setSessionId(data.session_id)
        setIsLoading(false)
      } catch (err) {
        console.error('セッション作成エラー:', err)
        setError(err instanceof Error ? err.message : 'セッション作成に失敗しました')
        setIsLoading(false)
      }
    }

    createSession()
  }, [apiUrl])

  if (isLoading) {
    return (
      <div className="app-loading">
        <p>セッションを作成中...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app-error">
        <h2>エラーが発生しました</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>再試行</button>
      </div>
    )
  }

  if (!sessionId) {
    return (
      <div className="app-error">
        <h2>セッションIDが取得できませんでした</h2>
        <button onClick={() => window.location.reload()}>再試行</button>
      </div>
    )
  }

  return (
    <div className="app">
      <ChatInterface sessionId={sessionId} apiUrl={apiUrl} />
    </div>
  )
}

export default App
