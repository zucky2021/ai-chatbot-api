/// アプリ設定（ビルド時注入）
///
/// `--dart-define` で環境ごとの値を注入します。
/// 例:
/// - API_BASE_URL: `http://localhost:8000`
/// - WS_BASE_URL: `ws://localhost:8000`
class AppConfig {
  static const String _apiBaseUrlFromEnv =
      String.fromEnvironment('API_BASE_URL', defaultValue: '');
  static const String _wsBaseUrlFromEnv =
      String.fromEnvironment('WS_BASE_URL', defaultValue: '');

  static String get apiBaseUrl =>
      _apiBaseUrlFromEnv.isNotEmpty ? _apiBaseUrlFromEnv : 'http://localhost:8000';

  static String get wsBaseUrl =>
      _wsBaseUrlFromEnv.isNotEmpty ? _wsBaseUrlFromEnv : 'ws://localhost:8000';
}

