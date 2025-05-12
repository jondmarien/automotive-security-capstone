import 'package:flutter/material.dart';

class AlertProvider extends ChangeNotifier {
  final List<String> _alerts = [];

  List<String> get alerts => _alerts;

  void addAlert(String alert) {
    _alerts.add(alert);
    notifyListeners();
  }
}