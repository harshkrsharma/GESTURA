import 'package:flutter/material.dart';

class ButtonWidget extends StatelessWidget {
  final VoidCallback onPressed;
  final Icon icon;
  const ButtonWidget({super.key, required this.onPressed, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.all(12),
      child: Material(
        shape: const CircleBorder(),
        elevation: 1,
        child: IconButton(onPressed: onPressed, icon: icon, iconSize: 28),
      ),
    );
  }
}
