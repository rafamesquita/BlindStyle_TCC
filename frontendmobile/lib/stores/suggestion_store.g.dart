// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'suggestion_store.dart';

// **************************************************************************
// StoreGenerator
// **************************************************************************

// ignore_for_file: non_constant_identifier_names, unnecessary_brace_in_string_interps, unnecessary_lambdas, prefer_expression_function_bodies, lines_longer_than_80_chars, avoid_as, avoid_annotating_with_dynamic, no_leading_underscores_for_local_identifiers

mixin _$SuggestionStore on _SuggestionStoreBase, Store {
  late final _$imageFileAtom = Atom(
    name: '_SuggestionStoreBase.imageFile',
    context: context,
  );

  @override
  XFile? get imageFile {
    _$imageFileAtom.reportRead();
    return super.imageFile;
  }

  @override
  set imageFile(XFile? value) {
    _$imageFileAtom.reportWrite(value, super.imageFile, () {
      super.imageFile = value;
    });
  }

  late final _$descriptionAtom = Atom(
    name: '_SuggestionStoreBase.description',
    context: context,
  );

  @override
  String? get description {
    _$descriptionAtom.reportRead();
    return super.description;
  }

  @override
  set description(String? value) {
    _$descriptionAtom.reportWrite(value, super.description, () {
      super.description = value;
    });
  }

  late final _$clothingDescriptionAtom = Atom(
    name: '_SuggestionStoreBase.clothingDescription',
    context: context,
  );

  @override
  ClothingDescription? get clothingDescription {
    _$clothingDescriptionAtom.reportRead();
    return super.clothingDescription;
  }

  @override
  set clothingDescription(ClothingDescription? value) {
    _$clothingDescriptionAtom.reportWrite(value, super.clothingDescription, () {
      super.clothingDescription = value;
    });
  }

  late final _$analysisResultAtom = Atom(
    name: '_SuggestionStoreBase.analysisResult',
    context: context,
  );

  @override
  Map<String, dynamic>? get analysisResult {
    _$analysisResultAtom.reportRead();
    return super.analysisResult;
  }

  @override
  set analysisResult(Map<String, dynamic>? value) {
    _$analysisResultAtom.reportWrite(value, super.analysisResult, () {
      super.analysisResult = value;
    });
  }

  late final _$isLoadingAtom = Atom(
    name: '_SuggestionStoreBase.isLoading',
    context: context,
  );

  @override
  bool get isLoading {
    _$isLoadingAtom.reportRead();
    return super.isLoading;
  }

  @override
  set isLoading(bool value) {
    _$isLoadingAtom.reportWrite(value, super.isLoading, () {
      super.isLoading = value;
    });
  }

  late final _$errorMessageAtom = Atom(
    name: '_SuggestionStoreBase.errorMessage',
    context: context,
  );

  @override
  String? get errorMessage {
    _$errorMessageAtom.reportRead();
    return super.errorMessage;
  }

  @override
  set errorMessage(String? value) {
    _$errorMessageAtom.reportWrite(value, super.errorMessage, () {
      super.errorMessage = value;
    });
  }

  late final _$suggestionsAtom = Atom(
    name: '_SuggestionStoreBase.suggestions',
    context: context,
  );

  @override
  ObservableList<SuggestedOutfit> get suggestions {
    _$suggestionsAtom.reportRead();
    return super.suggestions;
  }

  @override
  set suggestions(ObservableList<SuggestedOutfit> value) {
    _$suggestionsAtom.reportWrite(value, super.suggestions, () {
      super.suggestions = value;
    });
  }

  late final _$pickFromCameraAsyncAction = AsyncAction(
    '_SuggestionStoreBase.pickFromCamera',
    context: context,
  );

  @override
  Future<void> pickFromCamera() {
    return _$pickFromCameraAsyncAction.run(() => super.pickFromCamera());
  }

  late final _$pickFromGalleryAsyncAction = AsyncAction(
    '_SuggestionStoreBase.pickFromGallery',
    context: context,
  );

  @override
  Future<void> pickFromGallery() {
    return _$pickFromGalleryAsyncAction.run(() => super.pickFromGallery());
  }

  late final _$_analyzeAsyncAction = AsyncAction(
    '_SuggestionStoreBase._analyze',
    context: context,
  );

  @override
  Future<void> _analyze(XFile file) {
    return _$_analyzeAsyncAction.run(() => super._analyze(file));
  }

  late final _$generateSuggestionsAsyncAction = AsyncAction(
    '_SuggestionStoreBase.generateSuggestions',
    context: context,
  );

  @override
  Future<void> generateSuggestions(int itemId) {
    return _$generateSuggestionsAsyncAction.run(
      () => super.generateSuggestions(itemId),
    );
  }

  @override
  String toString() {
    return '''
imageFile: ${imageFile},
description: ${description},
clothingDescription: ${clothingDescription},
analysisResult: ${analysisResult},
isLoading: ${isLoading},
errorMessage: ${errorMessage},
suggestions: ${suggestions}
    ''';
  }
}
