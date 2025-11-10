import { useState, useRef, useEffect } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import './ChatInterface.css'

interface ChatInterfaceProps {
  sessionId: string
  userId?: string
  apiUrl?: string
}

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
}

export function ChatInterface({ sessionId, userId, apiUrl }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { isConnected, currentResponse, sendMessage, error } = useWebSocket({
    sessionId,
    userId,
    apiUrl,
    autoReconnect: false, // 自動再接続を無効化（エラーを防ぐため）
    onMessage: data => {
      if (data.type === 'processing') {
        setIsProcessing(true)
        // 新しいAIメッセージを開始
        setMessages(prev => [
          ...prev,
          {
            id: `ai-${Date.now()}`,
            type: 'ai',
            content: '',
            timestamp: new Date(),
          },
        ])
      } else if (data.type === 'done') {
        setIsProcessing(false)
      } else if (data.type === 'error') {
        setIsProcessing(false)
        alert(`エラー: ${data.message}`)
        console.error('WebSocketエラー:', data.message)
      }
    },
    onError: err => {
      console.error('WebSocketエラー:', err)
      alert(`エラーが発生しました: ${err.message}`)
    },
  })

  // currentResponseが更新されたら、最後のAIメッセージを更新
  useEffect(() => {
    if (currentResponse) {
      setMessages(prev => {
        const newMessages = [...prev]
        const lastMessage = newMessages[newMessages.length - 1]
        if (lastMessage && lastMessage.type === 'ai' && isProcessing) {
          lastMessage.content = currentResponse
        }
        return newMessages
      })
    }
  }, [currentResponse, isProcessing])

  // メッセージが更新されたら自動スクロール
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, currentResponse])

  const handleSend = () => {
    if (!inputMessage.trim() || !isConnected || isProcessing) {
      return
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    sendMessage(inputMessage, { language: 'ja' })
    setInputMessage('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>AI Chatbot</h2>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '● 接続中' : '○ 切断中'}
          </span>
          {error && <span className="error-message">エラー: {error.message}</span>}
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>メッセージを入力して会話を始めましょう</p>
          </div>
        )}
        {messages.map(message => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">
              {message.type === 'user' ? (
                <div className="user-message">{message.content}</div>
              ) : (
                <div className="ai-message">
                  {message.content || (isProcessing ? '応答を生成中...' : '')}
                </div>
              )}
            </div>
            <div className="message-timestamp">{message.timestamp.toLocaleTimeString()}</div>
          </div>
        ))}
        {isProcessing && currentResponse === '' && (
          <div className="message ai">
            <div className="message-content">
              <div className="ai-message">
                <span className="typing-indicator">考え中...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={inputMessage}
          onChange={e => setInputMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isConnected ? 'メッセージを入力...' : '接続中...'}
          disabled={!isConnected || isProcessing}
          maxLength={10000}
        />
        <button
          onClick={handleSend}
          disabled={!isConnected || !inputMessage.trim() || isProcessing}
        >
          送信
        </button>
      </div>
    </div>
  )
}
