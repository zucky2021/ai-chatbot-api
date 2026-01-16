import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:ai_chatbot/screens/chat_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 環境変数を読み込み
  try {
    await dotenv.load(fileName: '.env');
  } catch (e, st) {
    // .env が存在しない / 読み込み失敗してもアプリ自体は起動させる
    debugPrint('Failed to load .env: $e');
    debugPrintStack(stackTrace: st);
  }

  runApp(
    const ProviderScope(
      child: AIChatbotApp(),
    ),
  );
}

class AIChatbotApp extends StatelessWidget {
  const AIChatbotApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Chatbot',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 0,
        ),
      ),
      darkTheme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 0,
        ),
      ),
      themeMode: ThemeMode.system,
      home: const ChatScreen(),
    );
  }
}




