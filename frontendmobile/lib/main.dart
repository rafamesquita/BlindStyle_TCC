import 'package:blindstyle/di/service_locator.dart';
import 'package:flutter/material.dart';
import 'app.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  const backendUrl = 'URL';
  setupLocator(baseUrl: backendUrl);
  runApp(const MyApp());
}
