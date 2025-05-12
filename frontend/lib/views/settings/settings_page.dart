import 'package:flutter/material.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Text('Settings', style: TextStyle(fontSize: 32)),
          SizedBox(height: 16),
          Text('Settings Placeholder'),
        ],
      ),
    );
  }
}
