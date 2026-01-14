/// チャットメッセージモデル
class Message {
  final String id;
  final String content;
  final MessageRole role;
  final DateTime timestamp;
  final bool isStreaming;

  const Message({
    required this.id,
    required this.content,
    required this.role,
    required this.timestamp,
    this.isStreaming = false,
  });

  Message copyWith({
    String? id,
    String? content,
    MessageRole? role,
    DateTime? timestamp,
    bool? isStreaming,
  }) {
    return Message(
      id: id ?? this.id,
      content: content ?? this.content,
      role: role ?? this.role,
      timestamp: timestamp ?? this.timestamp,
      isStreaming: isStreaming ?? this.isStreaming,
    );
  }

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] as String? ?? '',
      content: json['content'] as String? ?? json['message'] as String? ?? '',
      role: json['role'] == 'assistant' ? MessageRole.assistant : MessageRole.user,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'role': role.name,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

/// メッセージの役割
enum MessageRole {
  user,
  assistant,
}




