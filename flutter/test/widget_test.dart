import 'package:flutter_test/flutter_test.dart';

import 'package:ai_chatbot/models/message.dart';
import 'package:ai_chatbot/models/session.dart';

void main() {
  group('Message', () {
    test('should create a Message from JSON', () {
      final json = {
        'id': '123',
        'content': 'Hello',
        'role': 'user',
        'timestamp': '2024-01-01T00:00:00.000Z',
      };

      final message = Message.fromJson(json);

      expect(message.id, '123');
      expect(message.content, 'Hello');
      expect(message.role, MessageRole.user);
    });

    test('should convert Message to JSON', () {
      final message = Message(
        id: '123',
        content: 'Hello',
        role: MessageRole.user,
        timestamp: DateTime(2024, 1, 1),
      );

      final json = message.toJson();

      expect(json['id'], '123');
      expect(json['content'], 'Hello');
      expect(json['role'], 'user');
    });

    test('should copy Message with new values', () {
      final original = Message(
        id: '123',
        content: 'Hello',
        role: MessageRole.user,
        timestamp: DateTime.now(),
      );

      final copied = original.copyWith(content: 'Updated');

      expect(copied.id, original.id);
      expect(copied.content, 'Updated');
      expect(copied.role, original.role);
    });
  });

  group('ChatSession', () {
    test('should create a ChatSession from JSON', () {
      final json = {
        'session_id': 'session-123',
        'user_id': 'user-456',
        'status': 'active',
        'created_at': '2024-01-01T00:00:00.000Z',
      };

      final session = ChatSession.fromJson(json);

      expect(session.sessionId, 'session-123');
      expect(session.userId, 'user-456');
      expect(session.status, 'active');
      expect(session.isActive, true);
    });

    test('should convert ChatSession to JSON', () {
      final session = ChatSession(
        sessionId: 'session-123',
        userId: 'user-456',
        status: 'active',
        createdAt: DateTime(2024, 1, 1),
      );

      final json = session.toJson();

      expect(json['session_id'], 'session-123');
      expect(json['user_id'], 'user-456');
      expect(json['status'], 'active');
    });
  });
}




