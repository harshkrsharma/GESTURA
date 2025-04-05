import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'package:image/image.dart' as img; // Import image package

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  runApp(CameraStreamApp(cameras: cameras));
}

class CameraStreamApp extends StatefulWidget {
  final List<CameraDescription> cameras;
  const CameraStreamApp({Key? key, required this.cameras}) : super(key: key);

  @override
  _CameraStreamAppState createState() => _CameraStreamAppState();
}

class _CameraStreamAppState extends State<CameraStreamApp> {
  late CameraController _cameraController;
  WebSocketChannel? _channel;
  bool _isStreaming = false;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    try {
      _cameraController = CameraController(
        widget.cameras[0],
        ResolutionPreset.low,
        enableAudio: false,
      );
      await _cameraController.initialize();
      setState(() {});
    } catch (e) {
      print("Error initializing camera: $e");
    }
  }

  void _initWebSocket() {
    _channel?.sink.close(); // Close previous WebSocket if exists
    _channel = WebSocketChannel.connect(
      Uri.parse("ws://192.168.81.170:8000/ws"),
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
  final int uvPixelStride = image.planes[1].bytesPerPixel ?? 1; // UV planes may be subsampled

  img.Image rgbImage = img.Image(width: width, height: height);

  for (int y = 0; y < height; y++) {
    for (int x = 0; x < width; x++) {
      final int yIndex = y * yRowStride + x;

      final int uvIndex =
          (y ~/ 2) * uvRowStride + (x ~/ 2) * uvPixelStride;

      final int yValue = yPlane[yIndex];
      final int uValue = uPlane[uvIndex] - 128;
      final int vValue = vPlane[uvIndex] - 128;

      // YUV to RGB conversion
      int r = (yValue + 1.370705 * vValue).clamp(0, 255).toInt();
      int g = (yValue - 0.698001 * vValue - 0.337633 * uValue).clamp(0, 255).toInt();
      int b = (yValue + 1.732446 * uValue).clamp(0, 255).toInt();

      rgbImage.setPixelRgb(x, y, r, g, b);
    }
  }

  return Uint8List.fromList(img.encodeJpg(rgbImage, quality: 80));
}


  void _stopStreaming() {
    if (_isStreaming) {
      _isStreaming = false;
      _cameraController.stopImageStream();
      _channel?.sink.close(status.goingAway);
      _channel = null;
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
        appBar: AppBar(title: const Text("Camera Streaming")),
        body: Column(
          children: [
            Expanded(
              child:
                  _cameraController.value.isInitialized
                      ? CameraPreview(_cameraController)
                      : const Center(child: CircularProgressIndicator()),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: _startStreaming,
                  child: const Text("Start Streaming"),
                ),
                ElevatedButton(
                  onPressed: _stopStreaming,
                  child: const Text("Stop Streaming"),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
