import 'package:flutter/material.dart';
import 'package:blindstyle/stores/theme_store.dart';
import 'package:blindstyle/di/service_locator.dart';
import 'package:flutter_mobx/flutter_mobx.dart';

class HeaderBar extends StatelessWidget implements PreferredSizeWidget {
  const HeaderBar({super.key});

  @override
  Widget build(BuildContext context) {
    final themeStore = getIt<ThemeStore>();

    return AppBar(
      centerTitle: true,
      title: const Text(
        'BlindStyle',
        style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.5),
      ),
      actions: [
        Observer(
          builder:
              (_) => IconButton(
                onPressed: themeStore.toggleTheme,
                icon: Icon(
                  themeStore.themeMode == ThemeMode.dark
                      ? Icons.light_mode
                      : Icons.dark_mode,
                ),
              ),
        ),
      ],
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}
