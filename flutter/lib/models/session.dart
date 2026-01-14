/// チャットセッションモデル
class ChatSession {
  final String sessionId;
  final String userId;
  final String status;
  final DateTime? createdAt;
  final Map<String, dynamic>? metadata;

  const ChatSession({
    required this.sessionId,
    required this.userId,
    required this.status,
    this.createdAt,
    this.metadata,
  });

  factory ChatSession.fromJson(Map<String, dynamic> json) {
    return ChatSession(
      sessionId: json['session_id'] as String,
      userId: json['user_id'] as String? ?? '',
      status: json['status'] as String? ?? 'active',
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'session_id': sessionId,
      'user_id': userId,
      'status': status,
      'created_at': createdAt?.toIso8601String(),
      'metadata': metadata,
    };
  }

  bool get isActive => status == 'active';
}




