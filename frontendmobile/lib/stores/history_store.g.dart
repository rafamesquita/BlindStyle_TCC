// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'history_store.dart';

// **************************************************************************
// StoreGenerator
// **************************************************************************

// ignore_for_file: non_constant_identifier_names, unnecessary_brace_in_string_interps, unnecessary_lambdas, prefer_expression_function_bodies, lines_longer_than_80_chars, avoid_as, avoid_annotating_with_dynamic, no_leading_underscores_for_local_identifiers

mixin _$HistoryStore on _HistoryStoreBase, Store {
  late final _$itemsAtom = Atom(
    name: '_HistoryStoreBase.items',
    context: context,
  );

  @override
  ObservableList<HistoryItem> get items {
    _$itemsAtom.reportRead();
    return super.items;
  }

  @override
  set items(ObservableList<HistoryItem> value) {
    _$itemsAtom.reportWrite(value, super.items, () {
      super.items = value;
    });
  }

  late final _$isLoadingAtom = Atom(
    name: '_HistoryStoreBase.isLoading',
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
    name: '_HistoryStoreBase.errorMessage',
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

  late final _$loadUserItemsAsyncAction = AsyncAction(
    '_HistoryStoreBase.loadUserItems',
    context: context,
  );

  @override
  Future<void> loadUserItems() {
    return _$loadUserItemsAsyncAction.run(() => super.loadUserItems());
  }

  late final _$getItemByIdAsyncAction = AsyncAction(
    '_HistoryStoreBase.getItemById',
    context: context,
  );

  @override
  Future<HistoryItem?> getItemById(int id) {
    return _$getItemByIdAsyncAction.run(() => super.getItemById(id));
  }

  @override
  String toString() {
    return '''
items: ${items},
isLoading: ${isLoading},
errorMessage: ${errorMessage}
    ''';
  }
}
