import 'package:flutter/material.dart';

class HistoryPage extends StatelessWidget {
  const HistoryPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Text('History', style: TextStyle(fontSize: 32)),
          SizedBox(height: 16),
          Text('History Placeholder'),
        ],
      ),
    );
  }
}
