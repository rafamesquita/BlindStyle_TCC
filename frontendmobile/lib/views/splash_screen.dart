import 'package:blindstyle/navigation/app_navigator.dart';
import 'package:flutter/material.dart';
import 'package:blindstyle/di/service_locator.dart';
import 'package:blindstyle/views/login_view.dart';
import 'package:blindstyle/views/camera_view.dart';
import '../stores/authentication_store.dart';

class SplashPage extends StatefulWidget {
  const SplashPage({super.key});

  @override
  State<SplashPage> createState() => _SplashPageState();
}

class _SplashPageState extends State<SplashPage> {
  final AuthenticationStore authStore = getIt<AuthenticationStore>();

  @override
  void initState() {
    super.initState();
    _loadSessionAndNavigate();
  }

  Future<void> _loadSessionAndNavigate() async {
    await authStore.loadSession();
    if (authStore.isLoggedIn) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const AppNavigator()),
      );
    } else {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const LoginView()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(body: Center(child: CircularProgressIndicator()));
  }
}
