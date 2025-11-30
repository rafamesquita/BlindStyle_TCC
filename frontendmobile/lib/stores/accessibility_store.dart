import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:mobx/mobx.dart';

part 'accessibility_store.g.dart';

class AccessibilityStore = _AccessibilityStoreBase with _$AccessibilityStore;

abstract class _AccessibilityStoreBase with Store {
  final FlutterTts _tts = FlutterTts();

  @observable
  double fontSizeFactor = 1.0;

  @observable
  bool highContrast = false;

  @observable
  bool largeFont = false;

  @observable
  bool ttsEnabled = false;

  @observable
  bool hapticFeedbackEnabled = false;

  @action
  void toggleHighContrast() => highContrast = !highContrast;

  @action
  void toggleLargeFont() => largeFont = !largeFont;

  @action
  void toggleTts() {
    ttsEnabled = !ttsEnabled;
  }

  @action
  void toggleHapticFeedback() {
    hapticFeedbackEnabled = !hapticFeedbackEnabled;
  }

  @action
  Future<void> speak(String text) async {
    if (!ttsEnabled) return;

    await _tts.setLanguage("pt-BR");
    await _tts.setSpeechRate(0.5);
    await _tts.setVolume(1.0);
    await _tts.setPitch(1.0);

    await _tts.speak(text);
  }

  @action
  Future<void> stopSpeaking() async {
    await _tts.stop();
  }

  @action
  void setFontSizeFactor(double value) {
    fontSizeFactor = value;
  }

  @action
  Future<void> triggerHaptic() async {
    try {
      await HapticFeedback.mediumImpact();
    } catch (_) {
      try {
        await HapticFeedback.vibrate();
      } catch (e) {
        print('Erro ao tentar feedback tátil: $e');
      }
    }
  }
}
