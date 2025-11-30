// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'accessibility_store.dart';

// **************************************************************************
// StoreGenerator
// **************************************************************************

// ignore_for_file: non_constant_identifier_names, unnecessary_brace_in_string_interps, unnecessary_lambdas, prefer_expression_function_bodies, lines_longer_than_80_chars, avoid_as, avoid_annotating_with_dynamic, no_leading_underscores_for_local_identifiers

mixin _$AccessibilityStore on _AccessibilityStoreBase, Store {
  late final _$fontSizeFactorAtom = Atom(
    name: '_AccessibilityStoreBase.fontSizeFactor',
    context: context,
  );

  @override
  double get fontSizeFactor {
    _$fontSizeFactorAtom.reportRead();
    return super.fontSizeFactor;
  }

  @override
  set fontSizeFactor(double value) {
    _$fontSizeFactorAtom.reportWrite(value, super.fontSizeFactor, () {
      super.fontSizeFactor = value;
    });
  }

  late final _$highContrastAtom = Atom(
    name: '_AccessibilityStoreBase.highContrast',
    context: context,
  );

  @override
  bool get highContrast {
    _$highContrastAtom.reportRead();
    return super.highContrast;
  }

  @override
  set highContrast(bool value) {
    _$highContrastAtom.reportWrite(value, super.highContrast, () {
      super.highContrast = value;
    });
  }

  late final _$largeFontAtom = Atom(
    name: '_AccessibilityStoreBase.largeFont',
    context: context,
  );

  @override
  bool get largeFont {
    _$largeFontAtom.reportRead();
    return super.largeFont;
  }

  @override
  set largeFont(bool value) {
    _$largeFontAtom.reportWrite(value, super.largeFont, () {
      super.largeFont = value;
    });
  }

  late final _$ttsEnabledAtom = Atom(
    name: '_AccessibilityStoreBase.ttsEnabled',
    context: context,
  );

  @override
  bool get ttsEnabled {
    _$ttsEnabledAtom.reportRead();
    return super.ttsEnabled;
  }

  @override
  set ttsEnabled(bool value) {
    _$ttsEnabledAtom.reportWrite(value, super.ttsEnabled, () {
      super.ttsEnabled = value;
    });
  }

  late final _$hapticFeedbackEnabledAtom = Atom(
    name: '_AccessibilityStoreBase.hapticFeedbackEnabled',
    context: context,
  );

  @override
  bool get hapticFeedbackEnabled {
    _$hapticFeedbackEnabledAtom.reportRead();
    return super.hapticFeedbackEnabled;
  }

  @override
  set hapticFeedbackEnabled(bool value) {
    _$hapticFeedbackEnabledAtom.reportWrite(
      value,
      super.hapticFeedbackEnabled,
      () {
        super.hapticFeedbackEnabled = value;
      },
    );
  }

  late final _$speakAsyncAction = AsyncAction(
    '_AccessibilityStoreBase.speak',
    context: context,
  );

  @override
  Future<void> speak(String text) {
    return _$speakAsyncAction.run(() => super.speak(text));
  }

  late final _$stopSpeakingAsyncAction = AsyncAction(
    '_AccessibilityStoreBase.stopSpeaking',
    context: context,
  );

  @override
  Future<void> stopSpeaking() {
    return _$stopSpeakingAsyncAction.run(() => super.stopSpeaking());
  }

  late final _$triggerHapticAsyncAction = AsyncAction(
    '_AccessibilityStoreBase.triggerHaptic',
    context: context,
  );

  @override
  Future<void> triggerHaptic() {
    return _$triggerHapticAsyncAction.run(() => super.triggerHaptic());
  }

  late final _$_AccessibilityStoreBaseActionController = ActionController(
    name: '_AccessibilityStoreBase',
    context: context,
  );

  @override
  void toggleHighContrast() {
    final _$actionInfo = _$_AccessibilityStoreBaseActionController.startAction(
      name: '_AccessibilityStoreBase.toggleHighContrast',
    );
    try {
      return super.toggleHighContrast();
    } finally {
      _$_AccessibilityStoreBaseActionController.endAction(_$actionInfo);
    }
  }

  @override
  void toggleLargeFont() {
    final _$actionInfo = _$_AccessibilityStoreBaseActionController.startAction(
      name: '_AccessibilityStoreBase.toggleLargeFont',
    );
    try {
      return super.toggleLargeFont();
    } finally {
      _$_AccessibilityStoreBaseActionController.endAction(_$actionInfo);
    }
  }

  @override
  void toggleTts() {
    final _$actionInfo = _$_AccessibilityStoreBaseActionController.startAction(
      name: '_AccessibilityStoreBase.toggleTts',
    );
    try {
      return super.toggleTts();
    } finally {
      _$_AccessibilityStoreBaseActionController.endAction(_$actionInfo);
    }
  }

  @override
  void toggleHapticFeedback() {
    final _$actionInfo = _$_AccessibilityStoreBaseActionController.startAction(
      name: '_AccessibilityStoreBase.toggleHapticFeedback',
    );
    try {
      return super.toggleHapticFeedback();
    } finally {
      _$_AccessibilityStoreBaseActionController.endAction(_$actionInfo);
    }
  }

  @override
  void setFontSizeFactor(double value) {
    final _$actionInfo = _$_AccessibilityStoreBaseActionController.startAction(
      name: '_AccessibilityStoreBase.setFontSizeFactor',
    );
    try {
      return super.setFontSizeFactor(value);
    } finally {
      _$_AccessibilityStoreBaseActionController.endAction(_$actionInfo);
    }
  }

  @override
  String toString() {
    return '''
fontSizeFactor: ${fontSizeFactor},
highContrast: ${highContrast},
largeFont: ${largeFont},
ttsEnabled: ${ttsEnabled},
hapticFeedbackEnabled: ${hapticFeedbackEnabled}
    ''';
  }
}
