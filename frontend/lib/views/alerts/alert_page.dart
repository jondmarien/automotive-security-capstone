import 'package:flutter/material.dart';

class AlertPage extends StatelessWidget {
  const AlertPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Text('Alerts', style: TextStyle(fontSize: 32)),
          SizedBox(height: 16),
          Text('Alerts Placeholder'),
        ],
      ),
    );
  }
}
