import 'package:flutter/material.dart';

class TranscriptWidget extends StatelessWidget {
  const TranscriptWidget({super.key, required this.detectedSign});
  final String detectedSign;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.width/3.3,
      width: MediaQuery.of(context).size.height/1.1,
      // color: Colors.grey,
      child: Center(child: Text("${detectedSign}" ,style: TextStyle(fontSize: 32, fontWeight: FontWeight.w600, color: Colors.grey.shade800),),),
    );
  }
}