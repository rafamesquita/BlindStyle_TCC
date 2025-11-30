import 'package:blindstyle/themes/colors.dart';
import 'package:flutter/material.dart';
import 'package:blindstyle/di/service_locator.dart';
import 'package:blindstyle/stores/accessibility_store.dart';

class AppTextStyles {
  static const header = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: AppColors.textPrimary,
    letterSpacing: 1.2,
  );

  static const subHeader = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: AppColors.textSecondary,
  );

  static const body = TextStyle(fontSize: 14, color: AppColors.textPrimary);

  static const button = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.bold,
    color: AppColors.white,
  );

  static TextStyle scaled(TextStyle style) {
    final accessibilityStore = getIt<AccessibilityStore>();
    final scale = accessibilityStore.fontSizeFactor;
    if (style.fontSize == null) return style;
    return style.copyWith(fontSize: style.fontSize! * scale);
  }
}
