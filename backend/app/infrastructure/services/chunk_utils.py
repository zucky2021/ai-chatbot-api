"""チャンクコンテンツ正規化ユーティリティ"""

from typing import Any


def normalize_chunk_content(content: Any) -> str:
    """
    LLMチャンクのコンテンツを文字列に正規化

    Google Generative AIのレスポンス形式に対応:
    - 辞書形式: {'type': 'text', 'text': '...', 'extras': {...}}
    - リスト形式: [{'type': 'text', 'text': '...'}, ...]
    - 文字列形式: '...'

    Args:
        content: チャンクのコンテンツ（辞書、リスト、文字列など）

    Returns:
        str: 正規化された文字列コンテンツ
    """
    # 辞書の場合、textキーからテキストを取得
    if isinstance(content, dict):
        # Google Generative AIのレスポンス形式: {'type': 'text', 'text': '...', 'extras': {...}}
        normalized = content.get("text", "") or content.get("content", "")
        # それでも空の場合は、辞書全体を文字列化（フォールバック）
        if not normalized:
            normalized = str(content.get("text", content))
        return str(normalized)

    # リストの場合は結合して文字列に変換
    if isinstance(content, list):
        # リストの各要素が辞書の場合は、textキーを抽出
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                text_parts.append(
                    item.get("text", "") or item.get("content", "")
                )
            else:
                text_parts.append(str(item))
        return "".join(text_parts)

    # 文字列でない場合は文字列に変換
    if not isinstance(content, str):
        return str(content)

    return content
