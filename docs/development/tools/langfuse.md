# LangFuse

LLMアプリケーションの観測性（Observability）と分析を提供するオープンソースプラットフォーム

- [公式サイト](https://langfuse.com/jp)
- [GitHub](https://github.com/langfuse/langfuse)

## 概要

- LLM（大規模言語モデル）を活用したアプリケーション開発において、観測性と分析機能を提供するプラットフォーム
- 開発者はモデルのパフォーマンスやコスト、応答時間などを詳細に把握し、アプリケーションの品質向上に役立てることが可能

## LangFuseを使用するメリット

### 1. **高度なトレーシング機能**

- アプリケーション内でのLLMの呼び出しや処理フローを詳細に追跡
- 各ステップのパフォーマンスやエラーを可視化
- 問題の特定やデバッグが容易になる

### 2. **プロンプト管理とバージョン管理**

- プロンプトのバージョン管理やチーム内での共有
- 再利用性の向上
- プロンプトの変更をコードのデプロイなしで迅速に反映
- A/Bテストによるプロンプトの最適化

### 3. **パフォーマンス指標の可視化**

- ワークフローごとの平均レイテンシ、スループット、エラー率などの主要なパフォーマンス指標をダッシュボードで確認
- SLAの維持やユーザー体験の最適化に役立つ

### 4. **エラー・例外のトラッキング**

- エラーメッセージ付きの失敗トレース一覧
- 特定エラータイプの発生頻度
- 時系列でのエラー発生状況を把握
- トラブルシューティングを加速

### 5. **コスト管理**

- モデルごとのトークン使用量を自動追跡
- コストを自動計算・可視化
- 予算管理とコスト最適化に役立つ

### 6. **LangChain/LangGraphとの統合**

- LangChainのコールバックで自動的にトレースを記録
- チェーン/グラフの実行フローを視覚的に確認
- 最小限のコード変更で統合可能

### 7. **セルフホスティング対応**

- 数分でセットアップが完了
- 自社のサーバーで運用可能
- セキュリティやコンプライアンスを重視する企業にとって大きなメリット
- データの完全制御が可能

## LangFuseを使用しない場合との比較

## 詳細比較表

| 項目                   | LangFuse使用                 | structlog + CloudWatch      |
| ---------------------- | ---------------------------- | --------------------------- |
| **LLMトレーシング**    | ✅ 自動                      | ⚠️ 手動実装が必要           |
| **トークン使用量追跡** | ✅ 自動                      | ⚠️ 手動実装が必要           |
| **コスト計算**         | ✅ 自動                      | ⚠️ 手動実装が必要           |
| **プロンプト管理**     | ✅ バージョン管理・A/Bテスト | ❌ なし                     |
| **ダッシュボード**     | ✅ 標準提供                  | ⚠️ 自前構築が必要           |
| **デバッグ機能**       | ✅ 詳細トレース・再現        | ⚠️ ログベースの分析         |
| **LangChain統合**      | ✅ コールバックで自動        | ⚠️ 手動実装が必要           |
| **セルフホスティング** | ✅ 対応                      | ✅ CloudWatch（マネージド） |
| **既存コード変更**     | ⚠️ コールバック追加          | ✅ 既に実装済み             |
| **学習コスト**         | ⚠️ 新ツールの習得            | ✅ 既存の知識で対応         |
| **運用コスト**         | ⚠️ 追加インフラ              | ✅ AWS標準サービス          |

## このプロジェクトでの推奨

### LangFuseを導入すべき場合

1. ✅ LLMのコスト管理が重要
2. ✅ プロンプトの最適化を頻繁に行う
3. ✅ 複数のプロンプトバージョンをA/Bテストしたい
4. ✅ チームでプロンプトを共有・管理したい
5. ✅ LLM呼び出しの詳細なデバッグが必要
6. ✅ LangChain/LangGraphを使用している（統合が容易）

### 現在の実装を継続すべき場合

1. ✅ シンプルなログで十分
2. ✅ 追加のインフラを避けたい
3. ✅ AWS標準サービスで完結させたい
4. ✅ 既存の実装で要件を満たしている
5. ✅ 小規模なプロジェクト

## ハイブリッドアプローチ

LangFuseを部分的に導入する方法：

- **開発環境**: LangFuseでデバッグとプロンプト開発
- **本番環境**: structlog + CloudWatchで運用監視
- **分析**: LangFuseのデータを定期的に確認してプロンプトを最適化

この方法なら、開発効率を上げつつ、本番環境のシンプルさを維持できます。

## 統合方法（参考）

### LangChainとの統合例

```python
from langfuse.callback import CallbackHandler
from langchain.callbacks import LangchainCallbackHandler

# LangFuseコールバックの初期化
langfuse_handler = CallbackHandler(
    public_key="your-public-key",
    secret_key="your-secret-key",
    host="https://cloud.langfuse.com"  # またはセルフホスティングURL
)

# LangChainチェーンにコールバックを追加
chain = prompt | llm
response = await chain.ainvoke(
    {"input": message.content},
    config={"callbacks": [langfuse_handler]}
)
```

### LangGraphとの統合例

<!-- FIXME:実装が完了したらソースコードの相対パスに変更 -->

```python
from langfuse.decorators import langfuse_context, observe

# デコレータを使用
@observe()
async def your_node(state: GraphState):
    # ノードの処理
    pass

# またはコンテキストマネージャーを使用
with langfuse_context():
    result = await graph.ainvoke(state)
```

## セットアップ（セルフホスティング）

### Docker Composeでの起動

```yaml
version: '3.8'
services:
  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - '3000:3000'
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/langfuse
      - NEXTAUTH_SECRET=your-secret
      - SALT=your-salt
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=langfuse
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 参考リンク

- [LangFuse公式ドキュメント](https://langfuse.com/docs)
- [LangChain統合ガイド](https://langfuse.com/docs/integrations/langchain)
- [LangGraph統合ガイド](https://langfuse.com/docs/integrations/langgraph)
- [セルフホスティングガイド](https://langfuse.com/docs/deployment/self-host)
