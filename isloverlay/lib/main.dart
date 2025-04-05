import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  static const platform = MethodChannel('com.example.isloverlay/overlay');

  Future<void> startOverlay() async {
    if (await Permission.systemAlertWindow.request().isGranted &&
        await Permission.camera.request().isGranted) {
      try {
        await platform.invokeMethod('startOverlay');
      } on PlatformException catch (e) {
        print("Error starting overlay: ${e.message}");
      }
    } else {
      print("Overlay permission not granted.");
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('Overlay Starter')),
        body: Center(
          child: ElevatedButton(
            onPressed: startOverlay,
            child: const Text("Start Floating Overlay"),
          ),
        ),
      ),
    );
  }
}
