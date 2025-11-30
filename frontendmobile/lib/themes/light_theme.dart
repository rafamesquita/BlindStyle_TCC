import 'package:flutter/material.dart';
import 'colors.dart';

final lightTheme = ThemeData(
  brightness: Brightness.light,
  primaryColor: AppColors.primary,
  scaffoldBackgroundColor: AppColors.background,

  appBarTheme: const AppBarTheme(
    backgroundColor: AppColors.white,
    foregroundColor: AppColors.primary,
  ),

  bottomNavigationBarTheme: const BottomNavigationBarThemeData(
    backgroundColor: AppColors.white,
    selectedItemColor: AppColors.primary,
    unselectedItemColor: Colors.grey,
  ),

  sliderTheme: const SliderThemeData(
    activeTrackColor: AppColors.primary,
    inactiveTrackColor: AppColors.white,
    thumbColor: AppColors.primary,
  ),

  cardTheme: const CardTheme(color: AppColors.white),

  colorScheme: const ColorScheme.light(
    primary: AppColors.primary,
    secondary: AppColors.white,
    surface: AppColors.background,
    onPrimary: AppColors.white,
    onSecondary: AppColors.textPrimary,
    onSurface: AppColors.textPrimary,
  ),

  textTheme: Typography.blackMountainView,

  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: AppColors.primary,
      foregroundColor: AppColors.white,
    ),
  ),
  bottomSheetTheme: const BottomSheetThemeData(
    backgroundColor: AppColors.background,
    modalBackgroundColor: AppColors.background,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
    ),
  ),
);
