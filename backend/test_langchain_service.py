"""LangChain AIサービスの動作確認スクリプト"""

import asyncio
from datetime import datetime
import sys

# パスを追加
sys.path.insert(0, ".")

from app.domain.value_objects.message import Message
from app.infrastructure.services.langchain_ai_service import LangChainAIService


async def test_basic_response():
    """基本的なレスポンス生成のテスト"""
    print("=" * 50)
    print("テスト1: 基本的なレスポンス生成")
    print("=" * 50)

    service = LangChainAIService()
    message = Message(
        content="こんにちは、元気ですか？",
        timestamp=datetime.now(),
        sender="test_user",
    )

    try:
        response = await service.generate_response(message, context="")
        print(f"✅ 成功: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False


async def test_with_context():
    """会話履歴を含むコンテキストのテスト"""
    print("\n" + "=" * 50)
    print("テスト2: 会話履歴を含むコンテキスト")
    print("=" * 50)

    service = LangChainAIService()
    context = "User: 私の名前は田中です\nAI: こんにちは、田中さん"

    message = Message(
        content="私の名前を覚えていますか？",
        timestamp=datetime.now(),
        sender="test_user",
    )

    try:
        response = await service.generate_response(message, context=context)
        print(f"✅ 成功: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return False


async def test_streaming():
    """ストリーミング応答のテスト"""
    print("\n" + "=" * 50)
    print("テスト3: ストリーミング応答")
    print("=" * 50)

    service = LangChainAIService()
    message = Message(
        content="1から10まで数えてください",
        timestamp=datetime.now(),
        sender="test_user",
    )

    try:
        print("ストリーミング開始:")
        chunks = []
        async for chunk in service.generate_stream(message, context=""):
            print(chunk, end="", flush=True)
            chunks.append(chunk)

        print(f"\n✅ 成功: {len(chunks)}個のチャンクを受信")
        return True
    except Exception as e:
        print(f"\n❌ エラー: {str(e)}")
        return False


async def test_history_building():
    """会話履歴の構築テスト"""
    print("\n" + "=" * 50)
    print("テスト4: 会話履歴の構築")
    print("=" * 50)

    service = LangChainAIService()
    context = """User: こんにちは
AI: こんにちは、何かお手伝いできることはありますか？
User: 今日の天気は？
AI: 申し訳ございませんが、リアルタイムの天気情報は取得できません。
User: わかりました"""

    try:
        history = service._build_history_from_context(context)
        messages = history.messages if hasattr(history, "messages") else []

        print(f"✅ 成功: {len(messages)}個のメッセージを構築")
        for i, msg in enumerate(messages, 1):
            msg_type = type(msg).__name__
            content = msg.content[:50] if hasattr(msg, "content") else str(msg)
            print(f"  {i}. {msg_type}: {content}...")
        return True
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """メイン関数"""
    print("LangChain AIサービスの動作確認を開始します...\n")

    results = []

    # 各テストを実行
    results.append(await test_basic_response())
    results.append(await test_with_context())
    results.append(await test_streaming())
    results.append(await test_history_building())

    # 結果サマリー
    print("\n" + "=" * 50)
    print("テスト結果サマリー")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"成功: {passed}/{total}")
    print(f"失敗: {total - passed}/{total}")

    if all(results):
        print("\n✅ すべてのテストが成功しました！")
        return 0
    else:
        print("\n❌ 一部のテストが失敗しました")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
