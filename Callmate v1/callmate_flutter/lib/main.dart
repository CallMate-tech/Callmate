import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';
import 'package:record/record.dart';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> with TickerProviderStateMixin {
  final record = AudioRecorder();
  bool isLoading = false;
  bool isRecording = false;
  bool isPlaying = false;
  final audioPlayer = AudioPlayer();
  late AnimationController _animationController;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: Duration(seconds: 1),
      lowerBound: 0.7,
      upperBound: 1.0,
    )..addListener(() {
      setState(() {});
    });

    audioPlayer.onPlayerComplete.listen((_) {
      stopAudio();
    });
  }

  Future<void> startRecording() async {
    if (isPlaying) return;

    if (await record.hasPermission()) {
      final directory = await getTemporaryDirectory();
      String filePath = '${directory.path}/input.wav';
      await record.start(
        const RecordConfig(encoder: AudioEncoder.wav),
        path: filePath,
      );
      setState(() {
        isRecording = true;
      });
    }
  }

  Future<void> stopRecording() async {
    if (isPlaying) {
      setState(() {
        isRecording = false;
      });
      return;
    }

    final path = await record.stop();
    setState(() {
      isRecording = false;
    });
    if (path != null) {
      await sendAudio(File(path));
    }
  }

  Future<void> sendAudio(File file) async {
    setState(() {
      isLoading = true;
    });
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('https://80f2-49-204-116-234.ngrok-free.app/process_audio'),
    );
    request.files.add(await http.MultipartFile.fromPath('file', file.path));
    var response = await request.send();
    if (response.statusCode == 200) {
      final dir = await getTemporaryDirectory();
      final outputPath = '${dir.path}/output.wav';
      final fileBytes = await response.stream.toBytes();
      File(outputPath).writeAsBytesSync(fileBytes);
      playAudio(outputPath);
    }
    setState(() {
      isLoading = false;
    });
  }

  Future<void> playAudio(String path) async {
    setState(() {
      isPlaying = true;
      isRecording = false;
    });
    _animationController.repeat(reverse: true);
    await audioPlayer.play(DeviceFileSource(path));
  }

  void stopAudio() {
    audioPlayer.stop();
    setState(() {
      isPlaying = false;
    });
    _animationController.stop();
  }

  @override
  void dispose() {
    audioPlayer.dispose();
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        backgroundColor: Colors.black,
        body: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Expanded(
              child: Center(
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    AnimatedContainer(
                      duration: Duration(milliseconds: 300),
                      width: isPlaying ? 200 * _animationController.value : 170,
                      height:
                          isPlaying ? 200 * _animationController.value : 170,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color.fromARGB(
                          255,
                          72,
                          243,
                          33,
                        ).withOpacity(isPlaying ? 0.9 : 0.6),
                      ),
                    ),
                    Icon(
                      Icons.podcasts_rounded,
                      size: 100,
                      color: Colors.white,
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: EdgeInsets.only(bottom: 50),
              child:
                  isLoading
                      ? CircularProgressIndicator(color: Colors.white)
                      : Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          GestureDetector(
                            onLongPress: startRecording,
                            onLongPressUp: stopRecording,
                            child: AnimatedContainer(
                              duration: Duration(milliseconds: 300),
                              width: 70,
                              height: 70,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: isPlaying ? Colors.grey : Colors.red,
                                boxShadow: [
                                  if (isRecording)
                                    BoxShadow(
                                      color: Colors.redAccent,
                                      blurRadius: 30,
                                      spreadRadius: 10,
                                    ),
                                ],
                              ),
                              child: Icon(
                                Icons.mic,
                                color: Colors.white,
                                size: 40,
                              ),
                            ),
                          ),
                          SizedBox(width: 180),
                          GestureDetector(
                            onTap: isPlaying ? stopAudio : null,
                            child: AnimatedContainer(
                              duration: Duration(milliseconds: 300),
                              width: 70,
                              height: 70,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: isPlaying ? Colors.red : Colors.grey,
                              ),
                              child: Icon(
                                Icons.close,
                                color: Colors.white,
                                size: 40,
                              ),
                            ),
                          ),
                        ],
                      ),
            ),
          ],
        ),
      ),
    );
  }
}
