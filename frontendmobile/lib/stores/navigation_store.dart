import 'package:mobx/mobx.dart';
import '../navigation/routes.dart';

part 'navigation_store.g.dart';

class NavigationStore = _NavigationStoreBase with _$NavigationStore;

abstract class _NavigationStoreBase with Store {
  @observable
  AppPage currentPage = AppPage.camera;

  @action
  void setPage(AppPage page) {
    currentPage = page;
  }
}
