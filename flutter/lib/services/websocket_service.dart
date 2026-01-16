import 'dart:async';
import 'dart:convert';

import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

/// WebSocketサービス
class WebSocketService {
  final String baseUrl;
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _channelSubscription;
  final StreamController<WebSocketMessage> _messageController =
      StreamController<WebSocketMessage>.broadcast();
  bool _isConnected = false;
  bool _isDisposed = false;

  WebSocketService({String? baseUrl})
      : baseUrl = baseUrl ?? dotenv.env['WS_BASE_URL'] ?? 'ws://localhost:8000';

  /// メッセージストリーム
  Stream<WebSocketMessage> get messageStream => _messageController.stream;

  /// 接続状態
  bool get isConnected => _isConnected;

  void _safeAdd(WebSocketMessage message) {
    if (_isDisposed) return;
    if (_messageController.isClosed) return;
    try {
      _messageController.add(message);
    } on StateError {
      // dispose競合等で controller が閉じられている場合は無視
    }
  }

  /// WebSocket接続
  Future<void> connect(String sessionId) async {
    if (_isDisposed) {
      throw StateError('WebSocketService は dispose 済みです');
    }

    if (_isConnected) {
      await disconnect();
    }

    final uri = Uri.parse('$baseUrl/api/chat/ws/$sessionId');

    try {
      _channel = WebSocketChannel.connect(uri);
      _isConnected = true;

      _channelSubscription = _channel!.stream.listen(
        (dynamic data) {
          _handleMessage(data);
        },
        onError: (dynamic error) {
          _isConnected = false;
          _safeAdd(WebSocketMessage.error(error.toString()));
        },
        onDone: () {
          _isConnected = false;
          _safeAdd(const WebSocketMessage.disconnected());
        },
      );

      _safeAdd(const WebSocketMessage.connected());
    } catch (e) {
      _isConnected = false;
      _safeAdd(WebSocketMessage.error(e.toString()));
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
            _safeAdd(WebSocketMessage.stream(content));
            break;
          case 'complete':
            final content = json['content'] as String? ?? '';
            _safeAdd(WebSocketMessage.complete(content));
            break;
          case 'error':
            final error = json['error'] as String? ?? 'Unknown error';
            _safeAdd(WebSocketMessage.error(error));
            break;
          default:
            _safeAdd(WebSocketMessage.unknown(data.toString()));
            break;
        }
      }
    } catch (e) {
      _safeAdd(WebSocketMessage.error('メッセージ解析エラー: $e'));
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
    final subscription = _channelSubscription;
    _channelSubscription = null;
    await subscription?.cancel();
    await _channel?.sink.close();
    _channel = null;
  }

  /// リソース解放
  void dispose() {
    if (_isDisposed) return;
    _isDisposed = true;
    _isConnected = false;

    // disconnect() は async のため await できないが、
    // controller を先に close すると onDone/onError から add されうる。
    // disconnect 完了後に close することで "Cannot add event after closing" を防ぐ。
    unawaited(
      disconnect().whenComplete(() async {
        if (_messageController.isClosed) return;
        await _messageController.close();
      }),
    );
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




