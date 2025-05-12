import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/alert_provider.dart';
import 'providers/settings_provider.dart';
import 'providers/signal_provider.dart';
import 'app.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AlertProvider()),
        ChangeNotifierProvider(create: (_) => SettingsProvider()),
        ChangeNotifierProvider(create: (_) => SignalProvider()),
      ],
      child: const App(),
    ),
  );
}
