"""DynamoDBセッションリポジトリ実装"""

from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from app.domain.entities.session import Session, SessionStatus
from app.domain.repositories import ISessionRepository
from app.infrastructure.config import settings


class DynamoDBSessionRepository(ISessionRepository):
    """DynamoDBセッションリポジトリ実装"""

    def __init__(self):
        # DynamoDBは非同期APIがないため、同期で実装
        self._dynamodb = boto3.resource(
            "dynamodb",
            endpoint_url=settings.AWS_ENDPOINT_URL,
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        # テーブルが存在しない場合は作成（LocalStack用）
        try:
            self._table = self._dynamodb.Table("chatbot-sessions")
            # テーブルの存在確認
            self._table.meta.client.describe_table(
                TableName="chatbot-sessions"
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # テーブルが存在しない場合は作成
                self._create_table()
                self._table = self._dynamodb.Table("chatbot-sessions")
            else:
                raise

    def _create_table(self):
        """テーブルを作成"""
        try:
            self._dynamodb.create_table(
                TableName="chatbot-sessions",
                KeySchema=[{"AttributeName": "session_id", "KeyType": "HASH"}],
                AttributeDefinitions=[
                    {"AttributeName": "session_id", "AttributeType": "S"}
                ],
                BillingMode="PAY_PER_REQUEST",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceInUseException":
                raise

    async def create(self, session: Session) -> Session:
        """セッションを作成（同期処理を非同期で実行）"""
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._create_sync, session)

    def _create_sync(self, session: Session) -> Session:
        """セッションを作成（同期実装）"""
        item = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "status": session.status.value,
            "metadata": session.metadata or {},
            "created_at": (
                session.created_at.isoformat()
                if session.created_at
                else datetime.now().isoformat()
            ),
            "updated_at": (
                session.updated_at.isoformat()
                if session.updated_at
                else datetime.now().isoformat()
            ),
        }

        if session.expires_at:
            item["expires_at"] = session.expires_at

        try:
            self._table.put_item(Item=item)
            return session
        except ClientError as e:
            raise RuntimeError(f"DynamoDBエラー: {str(e)}")

    async def get_by_id(self, session_id: str) -> Session | None:
        """IDでセッションを取得"""
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._get_by_id_sync, session_id
        )

    def _get_by_id_sync(self, session_id: str) -> Session | None:
        """IDでセッションを取得（同期実装）"""
        try:
            response = self._table.get_item(Key={"session_id": session_id})

            if "Item" not in response:
                return None

            item = response["Item"]
            return Session(
                session_id=item["session_id"],
                user_id=item["user_id"],
                status=SessionStatus(item["status"]),
                metadata=item.get("metadata"),
                created_at=datetime.fromisoformat(
                    item.get("created_at", datetime.now().isoformat())
                ),
                updated_at=datetime.fromisoformat(
                    item.get("updated_at", datetime.now().isoformat())
                ),
                expires_at=item.get("expires_at"),
            )
        except ClientError as e:
            raise RuntimeError(f"DynamoDBエラー: {str(e)}")

    async def get_by_user_id(self, user_id: str) -> list[Session]:
        """ユーザーIDでセッションを取得"""
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._get_by_user_id_sync, user_id
        )

    def _get_by_user_id_sync(self, user_id: str) -> list[Session]:
        """ユーザーIDでセッションを取得（同期実装）"""
        try:
            response = self._table.scan(
                FilterExpression="user_id = :user_id",
                ExpressionAttributeValues={":user_id": user_id},
            )

            sessions = []
            for item in response.get("Items", []):
                sessions.append(
                    Session(
                        session_id=item["session_id"],
                        user_id=item["user_id"],
                        status=SessionStatus(item["status"]),
                        metadata=item.get("metadata"),
                        created_at=datetime.fromisoformat(
                            item.get("created_at", datetime.now().isoformat())
                        ),
                        updated_at=datetime.fromisoformat(
                            item.get("updated_at", datetime.now().isoformat())
                        ),
                        expires_at=item.get("expires_at"),
                    )
                )

            return sessions
        except ClientError as e:
            raise RuntimeError(f"DynamoDBエラー: {str(e)}")

    async def update(self, session: Session) -> Session:
        """セッションを更新"""
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._update_sync, session)

    def _update_sync(self, session: Session) -> Session:
        """セッションを更新（同期実装）"""
        try:
            self._table.update_item(
                Key={"session_id": session.session_id},
                UpdateExpression="SET #status = :status, #metadata = :metadata, updated_at = :updated_at",
                ExpressionAttributeNames={
                    "#status": "status",
                    "#metadata": "metadata",
                },
                ExpressionAttributeValues={
                    ":status": session.status.value,
                    ":metadata": session.metadata or {},
                    ":updated_at": (
                        session.updated_at or datetime.now()
                    ).isoformat(),
                },
            )
            return session
        except ClientError as e:
            raise RuntimeError(f"DynamoDBエラー: {str(e)}")

    async def delete(self, session_id: str) -> None:
        """セッションを削除"""
        import asyncio

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._delete_sync, session_id)

    def _delete_sync(self, session_id: str) -> None:
        """セッションを削除（同期実装）"""
        try:
            self._table.delete_item(Key={"session_id": session_id})
        except ClientError as e:
            raise RuntimeError(f"DynamoDBエラー: {str(e)}")
