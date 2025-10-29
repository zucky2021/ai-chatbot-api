# コーディング規約

本ドキュメントは、AI Chatbot API プロジェクトにおけるコーディング規約を定義します。


## Git コミット

### コミットメッセージ

- **日本語**または**英語**で記述
- プレフィックスで種類を明示: `feat`, `fix`, `refactor`, `docs` など

```
feat: WebSocketチャット機能を追加
fix: DynamoDB接続エラーを修正
refactor: ログ出力処理を共通化
docs: READMEに環境変数の説明を追加
```

## コードレビュー

### チェックリスト

- [ ] 型アノテーションが適切に記載されているか
- [ ] エラーハンドリングが実装されているか
- [ ] テストが追加されているか
- [ ] ドキュメントが更新されているか
- [ ] 命名規則に従っているか
- [ ] 重複コードがないか
- [ ] セキュリティリスクがないか

## 参考リンク

- [PEP 8 -- Style Guide for Python Code](https://pep8.org/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/ja/tutorial/)

