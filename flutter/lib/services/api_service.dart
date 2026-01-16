import 'dart:convert';

import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

import 'package:ai_chatbot/models/session.dart';

/// APIサービス
class ApiService {
  static const Duration _timeout = Duration(seconds: 30);
  static const ApiException _timeoutException = ApiException(
    statusCode: 408,
    message: 'リクエストがタイムアウトしました',
  );

  final String baseUrl;
  final http.Client _client;

  ApiService({
    String? baseUrl,
    http.Client? client,
  })  : baseUrl = baseUrl ?? dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000',
        _client = client ?? http.Client();

  /// セッションを作成
  Future<ChatSession> createSession({Map<String, dynamic>? metadata}) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/api/chat/sessions'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'metadata': metadata ?? {'language': 'ja'},
      }),
    ).timeout(
      _timeout,
      onTimeout: () => throw _timeoutException,
    );

    if (response.statusCode != 200 && response.statusCode != 201) {
      throw ApiException(
        statusCode: response.statusCode,
        message: 'セッション作成に失敗しました',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return ChatSession.fromJson(data);
  }

  /// セッション情報を取得
  Future<ChatSession?> getSession(String sessionId) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/api/chat/sessions/$sessionId'),
    ).timeout(
      _timeout,
      onTimeout: () => throw _timeoutException,
    );

    if (response.statusCode == 404) {
      return null;
    }

    if (response.statusCode != 200) {
      throw ApiException(
        statusCode: response.statusCode,
        message: 'セッション取得に失敗しました',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return ChatSession.fromJson(data);
  }

  /// 会話履歴を取得
  Future<List<Map<String, dynamic>>> getConversationHistory(
    String sessionId,
  ) async {
    final response = await _client.get(
      Uri.parse('$baseUrl/api/chat/sessions/$sessionId/messages'),
    ).timeout(
      _timeout,
      onTimeout: () => throw _timeoutException,
    );

    if (response.statusCode != 200) {
      throw ApiException(
        statusCode: response.statusCode,
        message: '会話履歴の取得に失敗しました',
      );
    }

    final data = jsonDecode(response.body) as List<dynamic>;
    return data.cast<Map<String, dynamic>>();
  }

  /// ヘルスチェック
  Future<bool> healthCheck() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/api/health'),
      ).timeout(_timeout);
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  void dispose() {
    _client.close();
  }
}

/// API例外
class ApiException implements Exception {
  final int statusCode;
  final String message;

  const ApiException({
    required this.statusCode,
    required this.message,
  });

  @override
  String toString() => 'ApiException($statusCode): $message';
}
