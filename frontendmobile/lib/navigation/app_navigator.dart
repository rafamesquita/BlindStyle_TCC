import 'package:blindstyle/navigation/routes.dart';
import 'package:blindstyle/widgets/header_bar.dart';
import 'package:flutter/material.dart';
import 'package:flutter_mobx/flutter_mobx.dart';

import '../views/history_view.dart';
import '../views/camera_view.dart';
import '../views/settings_view.dart';
import '../stores/navigation_store.dart';
import '../widgets/bottom_nav_bar.dart';

class AppNavigator extends StatelessWidget {
  const AppNavigator({super.key});

  Widget _getPageWidget(AppPage page) {
    switch (page) {
      case AppPage.history:
        return HistoryView();
      case AppPage.camera:
        return CameraView();
      case AppPage.settings:
        return SettingsView();
    }
  }

  @override
  Widget build(BuildContext context) {
    final navStore = NavigationStore();

    return Observer(
      builder:
          (_) => Scaffold(
            appBar: const HeaderBar(),
            body: _getPageWidget(navStore.currentPage),
            bottomNavigationBar: BottomNavBar(
              currentPage: navStore.currentPage,
              onPageSelected: navStore.setPage,
            ),
          ),
    );
  }
}
