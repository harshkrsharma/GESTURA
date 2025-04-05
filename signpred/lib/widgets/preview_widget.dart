import 'package:flutter/material.dart';
import 'package:camera/camera.dart';

class CameraPreviewWidget extends StatelessWidget {
  final CameraController controller;

  const CameraPreviewWidget({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: SizedBox(
        height: MediaQuery.of(context).size.width /3.5,
        child: AspectRatio(
          aspectRatio:
              controller.value.aspectRatio, 
          child: CameraPreview(controller),
        ),
      ),
    );
  }
}
