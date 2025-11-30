import 'package:flutter/material.dart';

class AppColors {
  static const Color highContrastBackground = Colors.black;
  static const Color highContrastPrimary = Colors.yellow;
  static const Color highContrastSecondary = Colors.white;
  static const Color highContrastText = Colors.white;
}

final ThemeData highContrastTheme = ThemeData(
  brightness: Brightness.dark,
  scaffoldBackgroundColor: AppColors.highContrastBackground,
  primaryColor: AppColors.highContrastPrimary,
  colorScheme: const ColorScheme.highContrastDark(
    primary: AppColors.highContrastPrimary,
    secondary: AppColors.highContrastSecondary,
    background: AppColors.highContrastBackground,
    onPrimary: AppColors.highContrastText,
    onSecondary: AppColors.highContrastText,
    onBackground: AppColors.highContrastText,
  ),
  appBarTheme: const AppBarTheme(
    backgroundColor: AppColors.highContrastPrimary,
    foregroundColor: AppColors.highContrastText,
  ),
  textTheme: const TextTheme(
    titleLarge: TextStyle(
      color: AppColors.highContrastText,
      fontWeight: FontWeight.bold,
    ),
    bodyMedium: TextStyle(color: AppColors.highContrastText),
  ),
  elevatedButtonTheme: ElevatedButtonThemeData(
    style: ElevatedButton.styleFrom(
      backgroundColor: AppColors.highContrastPrimary,
      foregroundColor: AppColors.highContrastBackground,
      textStyle: const TextStyle(fontWeight: FontWeight.bold),
    ),
  ),
);
