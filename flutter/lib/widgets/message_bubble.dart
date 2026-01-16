import 'package:flutter/material.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:intl/intl.dart';

import 'package:ai_chatbot/models/message.dart';

/// メッセージバブルウィジェット
class MessageBubble extends StatelessWidget {
  final Message message;

  const MessageBubble({
    super.key,
    required this.message,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.role == MessageRole.user;
    final colorScheme = Theme.of(context).colorScheme;

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.8,
        ),
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isUser
              ? colorScheme.primaryContainer
              : colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isUser ? 16 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 16),
          ),
        ),
        child: Column(
          crossAxisAlignment:
              isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            // メッセージ内容
            if (isUser)
              Text(
                message.content,
                style: TextStyle(
                  color: colorScheme.onPrimaryContainer,
                ),
              )
            else
              MarkdownBody(
                data: message.content,
                styleSheet: MarkdownStyleSheet(
                  p: TextStyle(
                    color: colorScheme.onSurface,
                  ),
                  code: TextStyle(
                    backgroundColor: colorScheme.surfaceContainerHighest,
                    color: colorScheme.onSurface,
                  ),
                  codeblockDecoration: BoxDecoration(
                    color: colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                selectable: true,
              ),
            // ストリーミングインジケーター
            if (message.isStreaming) ...[
              const SizedBox(height: 8),
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: 12,
                    height: 12,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: colorScheme.primary,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '入力中...',
                    style: TextStyle(
                      fontSize: 12,
                      color: colorScheme.onSurface.withValues(alpha: (0.6 * 255).round()),
                    ),
                  ),
                ],
              ),
            ],
            // タイムスタンプ
            if (!message.isStreaming) ...[
              const SizedBox(height: 4),
              Text(
                DateFormat('HH:mm').format(message.timestamp),
                style: TextStyle(
                  fontSize: 10,
                  color: isUser
                      ? colorScheme.onPrimaryContainer.withValues(alpha: (0.6 * 255).round())
                      : colorScheme.onSurface.withValues(alpha: (0.6 * 255).round()),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}




