import 'package:flutter/material.dart';

class SignalProvider extends ChangeNotifier {
  double _signalStrength = 0.0;

  double get signalStrength => _signalStrength;

  void setSignalStrength(double value) {
    _signalStrength = value;
    notifyListeners();
  }
}