import 'package:flutter/material.dart';
import '../navigation/routes.dart';

class BottomNavBar extends StatelessWidget {
  final AppPage currentPage;
  final void Function(AppPage) onPageSelected;

  const BottomNavBar({
    super.key,
    required this.currentPage,
    required this.onPageSelected,
  });

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: pageIndexMap[currentPage]!,
      onTap: (index) => onPageSelected(indexPageMap[index]!),
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.photo_library),
          label: 'Histórico',
        ),
        BottomNavigationBarItem(icon: Icon(Icons.camera_alt), label: 'Foto'),
        BottomNavigationBarItem(
          icon: Icon(Icons.settings),
          label: 'Configurações',
        ),
      ],
    );
  }
}
