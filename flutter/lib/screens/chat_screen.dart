import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:ai_chatbot/models/message.dart';
import 'package:ai_chatbot/services/api_service.dart';
import 'package:ai_chatbot/services/websocket_service.dart';
import 'package:ai_chatbot/widgets/chat_input.dart';
import 'package:ai_chatbot/widgets/message_bubble.dart';

/// チャット画面
class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final List<Message> _messages = [];
  final ScrollController _scrollController = ScrollController();
  final ApiService _apiService = ApiService();
  final WebSocketService _wsService = WebSocketService();

  String? _sessionId;
  bool _isLoading = true;
  bool _isStreaming = false;
  String? _error;
  String _streamingContent = '';

  @override
  void initState() {
    super.initState();
    _initialize();
  }

  Future<void> _initialize() async {
    try {
      // セッション作成
      final session = await _apiService.createSession();
      _sessionId = session.sessionId;

      // WebSocket接続
      await _wsService.connect(_sessionId!);

      // メッセージストリームを購読
      _wsService.messageStream.listen(_handleWebSocketMessage);

      setState(() {
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _error = 'セッション作成に失敗しました: $e';
      });
    }
  }

  void _handleWebSocketMessage(WebSocketMessage message) {
    switch (message.type) {
      case WebSocketMessageType.stream:
        setState(() {
          _streamingContent += message.content ?? '';
          _isStreaming = true;
        });
        _scrollToBottom();
      case WebSocketMessageType.complete:
        setState(() {
          if (_streamingContent.isNotEmpty) {
            _messages.add(Message(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              content: _streamingContent,
              role: MessageRole.assistant,
              timestamp: DateTime.now(),
            ));
          }
          _streamingContent = '';
          _isStreaming = false;
        });
        _scrollToBottom();
      case WebSocketMessageType.error:
        setState(() {
          _error = message.error;
          _isStreaming = false;
          _streamingContent = '';
        });
      case WebSocketMessageType.disconnected:
        setState(() {
          _error = '接続が切断されました';
        });
      default:
        break;
    }
  }

  void _sendMessage(String content) {
    if (content.trim().isEmpty) return;

    // ユーザーメッセージを追加
    setState(() {
      _messages.add(Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        content: content,
        role: MessageRole.user,
        timestamp: DateTime.now(),
      ));
      _streamingContent = '';
    });

    // WebSocketでメッセージ送信
    _wsService.sendMessage(content);
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _wsService.dispose();
    _apiService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Chatbot'),
        actions: [
          if (_sessionId != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () {
                setState(() {
                  _messages.clear();
                  _error = null;
                });
              },
              tooltip: '会話をクリア',
            ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('セッションを作成中...'),
          ],
        ),
      );
    }

    if (_error != null && _sessionId == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red,
            ),
            const SizedBox(height: 16),
            Text(
              _error!,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.red),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  _isLoading = true;
                  _error = null;
                });
                _initialize();
              },
              child: const Text('再試行'),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        // メッセージリスト
        Expanded(
          child: _messages.isEmpty && !_isStreaming
              ? _buildEmptyState()
              : _buildMessageList(),
        ),
        // 入力エリア
        ChatInput(
          onSend: _sendMessage,
          enabled: !_isStreaming,
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.chat_bubble_outline,
            size: 64,
            color: Theme.of(context).colorScheme.primary.withOpacity(0.5),
          ),
          const SizedBox(height: 16),
          Text(
            'メッセージを入力してください',
            style: TextStyle(
              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageList() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: _messages.length + (_isStreaming ? 1 : 0),
      itemBuilder: (context, index) {
        if (index == _messages.length && _isStreaming) {
          // ストリーミング中のメッセージ
          return MessageBubble(
            message: Message(
              id: 'streaming',
              content: _streamingContent,
              role: MessageRole.assistant,
              timestamp: DateTime.now(),
              isStreaming: true,
            ),
          );
        }
        return MessageBubble(message: _messages[index]);
      },
    );
  }
}




