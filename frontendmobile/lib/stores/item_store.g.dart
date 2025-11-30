// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'item_store.dart';

// **************************************************************************
// StoreGenerator
// **************************************************************************

// ignore_for_file: non_constant_identifier_names, unnecessary_brace_in_string_interps, unnecessary_lambdas, prefer_expression_function_bodies, lines_longer_than_80_chars, avoid_as, avoid_annotating_with_dynamic, no_leading_underscores_for_local_identifiers

mixin _$ItemStore on _ItemStoreBase, Store {
  late final _$isLoadingAtom = Atom(
    name: '_ItemStoreBase.isLoading',
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
    name: '_ItemStoreBase.errorMessage',
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

  late final _$lastSavedItemAtom = Atom(
    name: '_ItemStoreBase.lastSavedItem',
    context: context,
  );

  @override
  Map<String, dynamic>? get lastSavedItem {
    _$lastSavedItemAtom.reportRead();
    return super.lastSavedItem;
  }

  @override
  set lastSavedItem(Map<String, dynamic>? value) {
    _$lastSavedItemAtom.reportWrite(value, super.lastSavedItem, () {
      super.lastSavedItem = value;
    });
  }

  late final _$saveItemAsyncAction = AsyncAction(
    '_ItemStoreBase.saveItem',
    context: context,
  );

  @override
  Future<bool> saveItem(File imageFile, String description) {
    return _$saveItemAsyncAction.run(
      () => super.saveItem(imageFile, description),
    );
  }

  @override
  String toString() {
    return '''
isLoading: ${isLoading},
errorMessage: ${errorMessage},
lastSavedItem: ${lastSavedItem}
    ''';
  }
}
