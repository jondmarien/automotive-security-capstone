import 'package:flutter/material.dart';

class SettingsProvider extends ChangeNotifier {
  double _sensitivity = 0.5;

  double get sensitivity => _sensitivity;

  void setSensitivity(double value) {
    _sensitivity = value;
    notifyListeners();
  }
}