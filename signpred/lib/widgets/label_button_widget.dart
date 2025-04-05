import 'package:flutter/material.dart';

class LabelButtonWidget extends StatelessWidget {
  final VoidCallback onPressed;
  final String label;
  const LabelButtonWidget({
    super.key,
    required this.onPressed,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      child: Text(label, style: TextStyle(color: Colors.grey.shade800)),
    );
  }
}
