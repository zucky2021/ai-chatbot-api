# Frontend (TypeScript/React)

## 基本

- こちらのサイトに則っていること
  - [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
  - [React Hooks](https://ja.react.dev/reference/react)

### ディレクトリ構造

```
frontend/src/
├── main.tsx              # エントリーポイント
├── App.tsx               # メインアプリケーション
├── App.css               # グローバルスタイル
├── index.css             # リセットCSS
└── assets/               # 静的ファイル
```

### 命名規則

#### 変数・関数名

- **キャメルケース**を使用: `camelCase`
- 関数名は動詞で始める: `handleSubmit`, `fetchData`, `validateInput`
- ブール値は `is`, `has`, `should` などで始める: `isLoading`, `hasError`

```typescript
// Good
function handleSubmit(event: FormEvent): void {
  // ...
}

let isConnecting = false;
const hasMessage = messages.length > 0;

// Bad
function Submit(): void {  // 動詞で始まっていない
  // ...
}
```

#### コンポーネント名

- **パスカルケース**を使用: `PascalCase`
- 名詞で始める: `ChatWindow`, `MessageInput`, `UserProfile`

```typescript
// Good
function ChatWindow(): JSX.Element {
  return <div>Chat Window</div>;
}

function MessageInput(): JSX.Element {
  return <input type="text" />;
}

// Bad
function chatWindow(): JSX.Element {  // パスカルケースではない
  return <div>Chat Window</div>;
}
```

#### 定数

- **全大文字**、**スネークケース**を使用: `UPPER_SNAKE_CASE`

```typescript
// Good
const API_BASE_URL = "http://localhost:8000";
const MAX_MESSAGE_LENGTH = 1000;

// Bad
const apiBaseUrl = "http://localhost:8000";  // 定数に見えない
```

### 型定義

- **型アノテーションを活用**: TypeScriptの型システムを最大限活用
- `any` は避ける: 必要な場合は `unknown` を使う

```typescript
// Good
interface ChatMessage {
  id: string;
  message: string;
  timestamp: Date;
  user_id: string;
}

function sendMessage(message: string): Promise<ChatMessage> {
  // ...
}

// Bad
function sendMessage(message: any): Promise<any> {  // anyを避ける
  // ...
}
```

#### 型の書き方

```typescript
// Good
interface User {
  id: string;
  name: string;
  email: string;
  created_at: Date;
}

type MessageStatus = "sent" | "delivered" | "read";

interface ChatMessage {
  id: string;
  content: string;
  status: MessageStatus;
  sender: User;
  timestamp: Date;
}

// Bad
interface ChatMessage {
  id: any;  // anyを避ける
  content: string;
  status: string;  // より具体的な型を定義すべき
  sender: any;
}
```

### コンポーネント設計

#### 関数コンポーネント

- 関数コンポーネントを使用（クラスコンポーネントは非推奨）
- Hooksを活用してステート管理

```typescript
// Good
import { useState, useEffect } from 'react';

interface ChatWindowProps {
  userId: string;
  sessionId: string;
}

function ChatWindow({ userId, sessionId }: ChatWindowProps): JSX.Element {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    // WebSocket接続ロジック
    const ws = new WebSocket('ws://localhost:8000/api/chat/ws');
    
    ws.onopen = () => {
      setIsConnected(true);
    };
    
    ws.onmessage = (event) => {
      const message: ChatMessage = JSON.parse(event.data);
      setMessages(prev => [...prev, message]);
    };
    
    ws.onerror = () => {
      setIsConnected(false);
    };
    
    return () => {
      ws.close();
    };
  }, []);
  
  return (
    <div>
      {/* UI */}
    </div>
  );
}

export default ChatWindow;

// Bad
class ChatWindow extends React.Component {  // クラスコンポーネント（非推奨）
  // ...
}
```

#### Props

- Propsの型を定義
- デフォルト値を使用する場合は `defaultProps` またはデフォルト引数を使用

```typescript
// Good
interface MessageBubbleProps {
  message: string;
  isOwn?: boolean;
  timestamp: Date;
}

function MessageBubble({
  message,
  isOwn = false,
  timestamp
}: MessageBubbleProps): JSX.Element {
  return (
    <div className={isOwn ? 'own-message' : 'other-message'}>
      <p>{message}</p>
      <span>{timestamp.toLocaleTimeString()}</span>
    </div>
  );
}

// Bad
function MessageBubble(props: any): JSX.Element {  // anyを避ける
  return <div>{props.message}</div>;
}
```

#### カスタムフック

- 再利用可能なロジックはカスタムフックに切り出す

```typescript
// Good
// hooks/useWebSocket.ts
import { useState, useEffect } from 'react';

interface UseWebSocketReturn {
  socket: WebSocket | null;
  isConnected: boolean;
  lastMessage: string | null;
  sendMessage: (message: string) => void;
}

function useWebSocket(url: string): UseWebSocketReturn {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<string | null>(null);
  
  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      setIsConnected(true);
      setSocket(ws);
    };
    
    ws.onmessage = (event) => {
      setLastMessage(event.data);
    };
    
    ws.onerror = () => {
      setIsConnected(false);
    };
    
    return () => {
      ws.close();
    };
  }, [url]);
  
  const sendMessage = (message: string): void => {
    if (socket?.readyState === WebSocket.OPEN) {
      socket.send(message);
    }
  };
  
  return { socket, isConnected, lastMessage, sendMessage };
}

export default useWebSocket;

// 使用例
function ChatWindow(): JSX.Element {
  const { isConnected, lastMessage, sendMessage } = useWebSocket(
    'ws://localhost:8000/api/chat/ws'
  );
  
  return (
    <div>
      {isConnected ? <p>接続中</p> : <p>未接続</p>}
      {/* メッセージ表示 */}
    </div>
  );
}
```

### エラーハンドリング

```typescript
// Good
async function fetchMessages(sessionId: string): Promise<ChatMessage[]> {
  try {
    const response = await fetch(`/api/chat/messages/${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.messages;
  } catch (error) {
    console.error('Failed to fetch messages:', error);
    throw error;
  }
}

// コンポーネント内
function ChatWindow(): JSX.Element {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    fetchMessages('session_123')
      .then(setMessages)
      .catch((err) => setError(err.message));
  }, []);
  
  if (error) {
    return <div>エラー: {error}</div>;
  }
  
  return <div>{/* メッセージ表示 */}</div>;
}
```

### CSS設計

#### クラス命名規則

- **CSS Modules** または **Tailwind CSS** を使用
- BEM方式を参考に命名

```typescript
// Good
// ChatWindow.module.css
.chatWindow {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.messageList {
  flex: 1;
  overflow-y: auto;
}

.messageBubble {
  padding: 10px;
  border-radius: 5px;
}

.messageBubble--own {
  background-color: #007bff;
  color: white;
}

// ChatWindow.tsx
import styles from './ChatWindow.module.css';

function ChatWindow(): JSX.Element {
  return (
    <div className={styles.chatWindow}>
      <div className={styles.messageList}>
        <div className={`${styles.messageBubble} ${styles.messageBubble--own}`}>
          Hello
        </div>
      </div>
    </div>
  );
}

// Bad
function ChatWindow(): JSX.Element {
  return (
    <div className="chat-window">  // インラインスタイルやグローバルクラス
      {/* ... */}
    </div>
  );
}
```

### テスト

```typescript
// __tests__/ChatWindow.test.tsx
import { render, screen } from '@testing-library/react';
import ChatWindow from '../ChatWindow';

describe('ChatWindow', () => {
  it('should render connected state', () => {
    render(<ChatWindow userId="user_123" sessionId="session_456" />);
    expect(screen.getByText('接続中')).toBeInTheDocument();
  });
  
  it('should display messages', () => {
    const messages = [
      { id: '1', message: 'Hello', timestamp: new Date() }
    ];
    render(<ChatWindow messages={messages} />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

### ツール・フォーマッター

- **Prettier**: コードフォーマッター
- **ESLint**: リンター

```bash
# フォーマット
pnpm prettier --write src/

# チェック
pnpm eslint src/
```
