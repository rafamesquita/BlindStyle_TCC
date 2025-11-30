// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'navigation_store.dart';

// **************************************************************************
// StoreGenerator
// **************************************************************************

// ignore_for_file: non_constant_identifier_names, unnecessary_brace_in_string_interps, unnecessary_lambdas, prefer_expression_function_bodies, lines_longer_than_80_chars, avoid_as, avoid_annotating_with_dynamic, no_leading_underscores_for_local_identifiers

mixin _$NavigationStore on _NavigationStoreBase, Store {
  late final _$currentPageAtom = Atom(
    name: '_NavigationStoreBase.currentPage',
    context: context,
  );

  @override
  AppPage get currentPage {
    _$currentPageAtom.reportRead();
    return super.currentPage;
  }

  @override
  set currentPage(AppPage value) {
    _$currentPageAtom.reportWrite(value, super.currentPage, () {
      super.currentPage = value;
    });
  }

  late final _$_NavigationStoreBaseActionController = ActionController(
    name: '_NavigationStoreBase',
    context: context,
  );

  @override
  void setPage(AppPage page) {
    final _$actionInfo = _$_NavigationStoreBaseActionController.startAction(
      name: '_NavigationStoreBase.setPage',
    );
    try {
      return super.setPage(page);
    } finally {
      _$_NavigationStoreBaseActionController.endAction(_$actionInfo);
    }
  }

  @override
  String toString() {
    return '''
currentPage: ${currentPage}
    ''';
  }
}
