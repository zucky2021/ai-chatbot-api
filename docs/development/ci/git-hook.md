# Git Hook

## 使用ツール

- [Husky](../../design/tech-stack.md#husky)
- [lint-staged](https://github.com/lint-staged/lint-staged) - ステージングされたファイルのみを対象にチェックを実行
- [Prettier](https://prettier.io/) - コードフォーマッター

## Pre-commit

コミット前に自動的に以下を実行します：

### 整形（Formatting）

以下のファイルタイプに対して Prettier による自動整形を実行：

- `*.md` - Markdown ファイル
- `*.tsx` - React TypeScript コンポーネント
- `*.ts` - TypeScript ファイル
- `*.json` - JSON ファイル

### 設定ファイル

- `.husky/pre-commit` - Git フック設定
- `package.json` の `lint-staged` セクション - 対象ファイルとコマンドの設定
- `.prettierrc.json` - Prettier の設定
- `.prettierignore` - Prettier の除外ファイル設定

### 使用方法

通常は自動実行されますが、手動で整形を実行する場合：

```bash
# 全ファイルを整形
pnpm format

# 整形チェックのみ（変更なし）
pnpm format:check
```
