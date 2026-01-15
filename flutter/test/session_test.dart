import 'package:flutter_test/flutter_test.dart';

import 'package:ai_chatbot/models/session.dart';

void main() {
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


