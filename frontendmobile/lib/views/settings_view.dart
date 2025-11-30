import 'package:blindstyle/themes/colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_mobx/flutter_mobx.dart';
import 'package:blindstyle/di/service_locator.dart';
import 'package:blindstyle/stores/accessibility_store.dart';

class SettingsView extends StatelessWidget {
  SettingsView({super.key});

  final AccessibilityStore accessibilityStore = getIt<AccessibilityStore>();

  TextStyle? _scaledTextStyle(TextStyle? baseStyle) {
    if (baseStyle == null) return null;
    return baseStyle.copyWith(
      fontSize: (baseStyle.fontSize ?? 14) * accessibilityStore.fontSizeFactor,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Observer(
          builder:
              (_) => ListView(
                children: [
                  ListTile(
                    title: Text(
                      'Tamanho da Fonte',
                      style: _scaledTextStyle(
                        Theme.of(context).textTheme.titleMedium,
                      ),
                    ),
                    subtitle: Slider(
                      value: accessibilityStore.fontSizeFactor,
                      onChanged: accessibilityStore.setFontSizeFactor,
                      min: 0.8,
                      max: 1.8,
                      divisions: 10,
                      label:
                          '${(accessibilityStore.fontSizeFactor * 100).round()}%',
                    ),
                    trailing: Text(
                      '${(accessibilityStore.fontSizeFactor * 100).round()}%',
                      style: _scaledTextStyle(
                        Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Theme.of(context).colorScheme.onSecondary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),

                  const Divider(),

                  SwitchListTile(
                    title: Text(
                      'Alto Contraste',
                      style: _scaledTextStyle(
                        Theme.of(context).textTheme.titleMedium,
                      ),
                    ),
                    value: accessibilityStore.highContrast,
                    onChanged: (_) => accessibilityStore.toggleHighContrast(),
                    activeColor: AppColors.primary,
                    secondary: const Icon(Icons.high_quality),
                  ),

                  const Divider(),

                  SwitchListTile(
                    title: Text(
                      'Leitura de Texto (TTS)',
                      style: _scaledTextStyle(
                        Theme.of(context).textTheme.titleMedium,
                      ),
                    ),
                    value: accessibilityStore.ttsEnabled,
                    onChanged: (_) => accessibilityStore.toggleTts(),
                    activeColor: AppColors.primary,
                    secondary: const Icon(Icons.record_voice_over),
                  ),

                  const Divider(),

                  SwitchListTile(
                    title: Text(
                      'Feedback Tátil',
                      style: _scaledTextStyle(
                        Theme.of(context).textTheme.titleMedium,
                      ),
                    ),
                    value: accessibilityStore.hapticFeedbackEnabled,
                    onChanged: (_) => accessibilityStore.toggleHapticFeedback(),
                    activeColor: AppColors.primary,
                    secondary: const Icon(Icons.vibration),
                  ),

                  const SizedBox(height: 24),

                  Center(
                    child: ElevatedButton.icon(
                      icon: const Icon(Icons.restore),
                      label: Observer(
                        builder: (_) => Text('Resetar Configurações'),
                      ),
                      onPressed: () {
                        accessibilityStore.setFontSizeFactor(1.0);
                        if (accessibilityStore.highContrast) {
                          accessibilityStore.toggleHighContrast();
                        }
                        if (accessibilityStore.ttsEnabled) {
                          accessibilityStore.toggleTts();
                        }
                        if (accessibilityStore.hapticFeedbackEnabled) {
                          accessibilityStore.toggleHapticFeedback();
                        }
                      },
                    ),
                  ),
                ],
              ),
        ),
      ),
    );
  }
}
