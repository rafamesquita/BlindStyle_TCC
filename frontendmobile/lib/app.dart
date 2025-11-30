import 'package:flutter/material.dart';
import 'package:blindstyle/stores/theme_store.dart';
import 'package:blindstyle/stores/accessibility_store.dart';
import 'package:blindstyle/themes/high_contrast_theme.dart';
import 'package:blindstyle/themes/dark_theme.dart';
import 'package:blindstyle/themes/light_theme.dart';
import 'package:blindstyle/di/service_locator.dart';
import 'package:flutter_mobx/flutter_mobx.dart';
import 'package:blindstyle/views/splash_screen.dart';

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeStore = getIt<ThemeStore>();
    final accessibilityStore = getIt<AccessibilityStore>();

    return Observer(
      builder: (_) {
        final baseTheme =
            accessibilityStore.highContrast
                ? highContrastTheme
                : (themeStore.themeMode == ThemeMode.dark
                    ? darkTheme
                    : lightTheme);
        final textScaleFactor = accessibilityStore.largeFont ? 1.3 : 1.0;

        return MaterialApp(
          title: 'BlindStyle',
          theme: baseTheme,
          darkTheme: darkTheme,
          themeMode: themeStore.themeMode,
          builder: (context, child) {
            return MediaQuery(
              data: MediaQuery.of(
                context,
              ).copyWith(textScaleFactor: textScaleFactor),
              child: child!,
            );
          },
          home: const SplashPage(),
        );
      },
    );
  }
}
