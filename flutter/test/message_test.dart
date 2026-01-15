import 'package:flutter_test/flutter_test.dart';

import 'package:ai_chatbot/models/message.dart';

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
        timestamp: DateTime.utc(2024, 1, 1),
      );

      final json = message.toJson();

      expect(json['id'], '123');
      expect(json['content'], 'Hello');
      expect(json['role'], 'user');
      expect(json['timestamp'], '2024-01-01T00:00:00.000Z');
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
}


