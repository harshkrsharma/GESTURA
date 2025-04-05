import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:flutter/services.dart';
import 'package:signpred/widgets/button_widget.dart';
import 'package:signpred/widgets/label_button_widget.dart';
import 'package:signpred/widgets/preview_widget.dart';
import 'package:signpred/widgets/title_widget.dart';
import 'package:signpred/widgets/transcript_widget.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'package:image/image.dart' as img;
import 'package:http/http.dart' as http;
import 'package:flutter_tts/flutter_tts.dart';

class CameraStreamApp extends StatefulWidget {
  const CameraStreamApp({super.key});

  @override
  _CameraStreamAppState createState() => _CameraStreamAppState();
}

class _CameraStreamAppState extends State<CameraStreamApp> {
  late final List<CameraDescription> cameras;
  int _cameraIndex = 0;
  late CameraController _cameraController;
  WebSocketChannel? _channel;
  bool _isStreaming = false;
  String _detectedSign = "Waiting for sign...";
  bool _isCameraInitialized = false;
  List<String> _detectedWords = [];
  FlutterTts flutterTts = FlutterTts();

  @override
  void initState() {
    super.initState();
    _getCameras();
  }

  Future<void> _getCameras() async {
    cameras = await availableCameras();
    if (cameras.isNotEmpty) {
      _cameraController = CameraController(
        cameras[_cameraIndex],
        ResolutionPreset.low,
        enableAudio: false,
      );
      await _cameraController.initialize();
      setState(() {
        _isCameraInitialized = true;
      });
    } else {
      print("No cameras found");
    }
  }

  void _switchCamera() async {
    print("camera switched");
    if (cameras.length > 1) {
      _cameraIndex ^= 1;
      await _cameraController.dispose();
      _cameraController = CameraController(
        cameras[_cameraIndex],
        ResolutionPreset.low,
        enableAudio: false,
      );
      await _cameraController.initialize();
      setState(() {});
    } else {
      print("You only have one camera");
    }
  }

  void _initWebSocket() {
    _channel?.sink.close();
    _channel = WebSocketChannel.connect(
      Uri.parse("ws://192.168.17.170:8000/ws"),
    );

    _channel?.stream.listen(
      (message) {
        try {
          final List<dynamic> receivedWords = jsonDecode(
            message,
          ); // Decode the incoming JSON
          setState(() {
            _detectedWords =
                receivedWords
                    .cast<String>(); // Replace the list with received words
            _detectedSign = _detectedWords.toString();
          });
          print("Updated Detected Words: $_detectedWords");
        } catch (e) {
          print("Error parsing WebSocket message: $e");
        }
      },
      onError: (error) {
        print("WebSocket error: $error");
      },
    );
  }

  void _startStreaming() {
    if (!_cameraController.value.isInitialized) {
      print("Camera not initialized yet.");
      return;
    }

    _initWebSocket();
    _isStreaming = true;

    _cameraController.startImageStream((CameraImage image) async {
      if (!_isStreaming || _channel == null) return;

      try {
        Uint8List jpgBytes = _convertYToJpg(image);
        _channel?.sink.add(jpgBytes);
      } catch (e) {
        print("Error processing frame: $e");
      }
    });
  }

  Uint8List _convertYToJpg(CameraImage image) {
    final int width = image.width;
    final int height = image.height;
    final Uint8List yPlane = image.planes[0].bytes;
    final Uint8List uPlane = image.planes[1].bytes;
    final Uint8List vPlane = image.planes[2].bytes;
    final int yRowStride = image.planes[0].bytesPerRow;
    final int uvRowStride = image.planes[1].bytesPerRow;
    final int uvPixelStride = image.planes[1].bytesPerPixel ?? 1;
    img.Image rgbImage = img.Image(width: width, height: height);

    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        final int yIndex = y * yRowStride + x;
        final int uvIndex = (y ~/ 2) * uvRowStride + (x ~/ 2) * uvPixelStride;
        final int yValue = yPlane[yIndex];
        final int uValue = uPlane[uvIndex] - 128;
        final int vValue = vPlane[uvIndex] - 128;
        int r = (yValue + 1.370705 * vValue).clamp(0, 255).toInt();
        int g =
            (yValue - 0.698001 * vValue - 0.337633 * uValue)
                .clamp(0, 255)
                .toInt();
        int b = (yValue + 1.732446 * uValue).clamp(0, 255).toInt();
        rgbImage.setPixelRgb(x, y, r, g, b);
      }
    }
    return Uint8List.fromList(img.encodeJpg(rgbImage, quality: 80));
  }

  void _stopStreaming() {
    setState(() {
      _detectedSign = "Waiting for sign...";
    });
    if (_isStreaming) {
      _isStreaming = false;
      _cameraController.stopImageStream();
      _channel?.sink.close(status.goingAway);
      _channel = null;
    }
  }

  void _speak() async {
    var result = await flutterTts.speak(_detectedSign);
    // if (result == 1) setState(() => ttsState = TtsState.playing);
  }

  void _translate() async {
    final uri = Uri.parse("http://192.168.17.170:8000/nlp_process");

    final response = await http.post(
      uri,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "words": _detectedWords,
      }), // Use the updated detected words list
    );

    if (response.statusCode == 200) {
      final responseData = jsonDecode(response.body);
      setState(() {
        _detectedSign = responseData['sentence'] ?? "Translation unavailable";
      });
      print("Generated Sentence: ${responseData['sentence']}");
    } else {
      print("Failed to generate sentence from detected words.");
    }
  }

  @override
  void dispose() {
    _stopStreaming();
    _cameraController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: Padding(
          padding: EdgeInsets.all(32),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Column(
                mainAxisAlignment: MainAxisAlignment.start,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TitleWidget(),
                  _isCameraInitialized
                      ? CameraPreviewWidget(controller: _cameraController)
                      : const Center(child: CircularProgressIndicator()),
                ],
              ),
              SizedBox(width: 20),
              Column(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  ButtonWidget(
                    onPressed: _translate,
                    icon: Icon(Icons.accessibility_new_rounded),
                  ),
                  ButtonWidget(
                    onPressed: _speak,
                    icon: Icon(Icons.volume_up_rounded),
                  ),
                  ButtonWidget(
                    onPressed: _switchCamera,
                    icon: Icon(Icons.cameraswitch),
                  ),
                ],
              ),
              SizedBox(width: 20),
              Column(
                children: [
                  TranscriptWidget(detectedSign: _detectedSign),
                  Spacer(),
                  Row(
                    children: [
                      LabelButtonWidget(
                        onPressed: _startStreaming,
                        label: "Start Streaming",
                      ),
                      SizedBox(width: 20),
                      LabelButtonWidget(
                        onPressed: _stopStreaming,
                        label: "Stop Streaming",
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
