import 'package:flutter/material.dart';
import 'colors.dart';

final darkTheme = ThemeData(
  brightness: Brightness.dark,
  primaryColor: AppColors.textPrimary,
  scaffoldBackgroundColor: AppColors.darkBackground,

  appBarTheme: const AppBarTheme(
    backgroundColor: AppColors.textPrimary,
    foregroundColor: AppColors.white,
  ),

  bottomNavigationBarTheme: const BottomNavigationBarThemeData(
    backgroundColor: AppColors.textPrimary,
    selectedItemColor: AppColors.white,
    unselectedItemColor: AppColors.textSecondary,
  ),

  sliderTheme: const SliderThemeData(
    activeTrackColor: AppColors.white,
    inactiveTrackColor: AppColors.textPrimary,
    thumbColor: AppColors.white,
  ),

  cardTheme: const CardTheme(color: AppColors.textPrimary),

  colorScheme: const ColorScheme.dark(
    primary: AppColors.textPrimary,
    secondary: AppColors.white,
    surface: AppColors.textPrimary,
    onPrimary: AppColors.white,
    onSecondary: AppColors.white,
    onSurface: Colors.white,
  ),

  textTheme: Typography.whiteMountainView,

  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: AppColors.textPrimary,
      foregroundColor: AppColors.white,
    ),
  ),
  bottomSheetTheme: const BottomSheetThemeData(
    backgroundColor: AppColors.darkBackground,
    modalBackgroundColor: AppColors.darkBackground,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
    ),
  ),
);
