import 'package:flutter/material.dart';

class DashboardPage extends StatelessWidget {
  const DashboardPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Text('Dashboard', style: TextStyle(fontSize: 32)),
          SizedBox(height: 16),
          Text('Signal Strength Placeholder'),
        ],
      ),
    );
  }
}
