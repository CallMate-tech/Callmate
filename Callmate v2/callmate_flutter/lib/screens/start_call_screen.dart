import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'voice_chat_screen.dart';

class StartCallScreen extends StatelessWidget {
  final String userId;
  const StartCallScreen({super.key, required this.userId});

  Future<void> startCall() async {
    print("Start Call button pressed");
    await http.post(
      Uri.parse("https://b01c-49-204-116-234.ngrok-free.app/start_call"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"user_id": userId}),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green,
            padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          ),
          onPressed: () async {
            await startCall();
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => VoiceChatScreen(userId: userId),
              ),
            );
          },
          child: Text("Start Call", style: TextStyle(fontSize: 20)),
        ),
      ),
    );
  }
}
