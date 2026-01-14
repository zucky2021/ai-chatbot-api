import 'dart:async';
import 'dart:convert';

import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

/// WebSocketサービス
class WebSocketService {
  final String baseUrl;
  WebSocketChannel? _channel;
  final StreamController<WebSocketMessage> _messageController =
      StreamController<WebSocketMessage>.broadcast();
  bool _isConnected = false;

  WebSocketService({String? baseUrl})
      : baseUrl = baseUrl ?? dotenv.env['WS_BASE_URL'] ?? 'ws://localhost:8000';

  /// メッセージストリーム
  Stream<WebSocketMessage> get messageStream => _messageController.stream;

  /// 接続状態
  bool get isConnected => _isConnected;

  /// WebSocket接続
  Future<void> connect(String sessionId) async {
    if (_isConnected) {
      await disconnect();
    }

    final uri = Uri.parse('$baseUrl/api/chat/ws/$sessionId');

    try {
      _channel = WebSocketChannel.connect(uri);
      _isConnected = true;

      _channel!.stream.listen(
        (dynamic data) {
          _handleMessage(data);
        },
        onError: (dynamic error) {
          _messageController.add(WebSocketMessage.error(error.toString()));
          _isConnected = false;
        },
        onDone: () {
          _isConnected = false;
          _messageController.add(const WebSocketMessage.disconnected());
        },
      );

      _messageController.add(const WebSocketMessage.connected());
    } catch (e) {
      _isConnected = false;
      _messageController.add(WebSocketMessage.error(e.toString()));
      rethrow;
    }
  }

  /// メッセージ処理
  void _handleMessage(dynamic data) {
    try {
      if (data is String) {
        final json = jsonDecode(data) as Map<String, dynamic>;
        final type = json['type'] as String?;

        switch (type) {
          case 'stream':
            final content = json['content'] as String? ?? '';
            _messageController.add(WebSocketMessage.stream(content));
          case 'complete':
            final content = json['content'] as String? ?? '';
            _messageController.add(WebSocketMessage.complete(content));
          case 'error':
            final error = json['error'] as String? ?? 'Unknown error';
            _messageController.add(WebSocketMessage.error(error));
          default:
            _messageController.add(WebSocketMessage.unknown(data));
        }
      }
    } catch (e) {
      _messageController.add(WebSocketMessage.error('メッセージ解析エラー: $e'));
    }
  }

  /// メッセージ送信
  void sendMessage(String message) {
    if (!_isConnected || _channel == null) {
      throw StateError('WebSocketが接続されていません');
    }

    final payload = jsonEncode({
      'type': 'message',
      'content': message,
    });

    _channel!.sink.add(payload);
  }

  /// 切断
  Future<void> disconnect() async {
    _isConnected = false;
    await _channel?.sink.close();
    _channel = null;
  }

  /// リソース解放
  void dispose() {
    disconnect();
    _messageController.close();
  }
}

/// WebSocketメッセージ
class WebSocketMessage {
  final WebSocketMessageType type;
  final String? content;
  final String? error;

  const WebSocketMessage._({
    required this.type,
    this.content,
    this.error,
  });

  const WebSocketMessage.connected()
      : this._(type: WebSocketMessageType.connected);

  const WebSocketMessage.disconnected()
      : this._(type: WebSocketMessageType.disconnected);

  const WebSocketMessage.stream(String content)
      : this._(type: WebSocketMessageType.stream, content: content);

  const WebSocketMessage.complete(String content)
      : this._(type: WebSocketMessageType.complete, content: content);

  const WebSocketMessage.error(String error)
      : this._(type: WebSocketMessageType.error, error: error);

  const WebSocketMessage.unknown(String content)
      : this._(type: WebSocketMessageType.unknown, content: content);
}

/// WebSocketメッセージタイプ
enum WebSocketMessageType {
  connected,
  disconnected,
  stream,
  complete,
  error,
  unknown,
}




