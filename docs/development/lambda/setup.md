# Lambda 環境構築手順

## 前提条件

**Check install**:

- Python 3.12 以上
- `uv`（Python パッケージマネージャー）
- AWS CLI
- AWS SAM CLI
- AWS CDK CLI

```sh
python3 --version
uv --version
aws --version
sam --version
cdk --version
```

## 手順

### 1. パッケージインストール

```sh
cd lambda
uv sync --all-extras
```

## 2. AWS CLI のセットアップ

- プロファイル設定

- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` などを設定
  - 開発環境では LocalStack を使う場合は、ダミー値で構いません）

```sh
aws configure
```

- e.g.

```sh
aws configure
AWS Access Key ID [None]: dummy-access-key
AWS Secret Access Key [None]: dummy-secret-access-key
Default region name [None]: ap-northeast-1
Default output format [None]: json
```

## コンテナ起動

```sh
docker compose up
```

## 参考

- [LocalStack document](../tools/localstack.md)
- [compose.yaml](/compose.yml)
