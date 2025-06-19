import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';
import 'screens/start_call_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  String? userId = prefs.getString('user_id');

  if (userId == null) {
    userId = Uuid().v4();
    await prefs.setString('user_id', userId);
  }

  runApp(MyApp(userId: userId));
}

class MyApp extends StatelessWidget { 
  final String userId;
  const MyApp({super.key, required this.userId});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Tamil Call',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(),
      home: StartCallScreen(userId: userId),
    );
  }
}
