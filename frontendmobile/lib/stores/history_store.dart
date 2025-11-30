import 'package:blindstyle/stores/authentication_store.dart';
import 'package:mobx/mobx.dart';
import 'package:blindstyle/data/services/item_service.dart';
import '../di/service_locator.dart';

part 'history_store.g.dart';

class HistoryStore = _HistoryStoreBase with _$HistoryStore;

class HistoryItem {
  final int id;
  final String imagePath;
  final String description;

  HistoryItem({
    required this.imagePath,
    required this.description,
    required this.id,
  });
}

abstract class _HistoryStoreBase with Store {
  final ItemService _itemService = getIt<ItemService>();
  final AuthenticationStore _authStore = getIt<AuthenticationStore>();

  @observable
  ObservableList<HistoryItem> items = ObservableList.of([]);

  @observable
  bool isLoading = false;

  @observable
  String? errorMessage;

  @action
  Future<void> loadUserItems() async {
    isLoading = true;
    errorMessage = null;

    try {
      final token = _authStore.accessToken!;
      final response = await _itemService.getItemsList(token: token);

      items = ObservableList.of(
        (response['items'] as List).map((item) {
          final base64Image = item['image_url']?.toString() ?? '';
          final description =
              item['description']?.toString() ?? 'Sem descrição';
          final id = item['id'] ?? 'Sem descrição';

          return HistoryItem(
            imagePath: base64Image,
            description: description,
            id: id,
          );
        }).toList(),
      );
    } catch (e) {
      errorMessage = 'Erro ao carregar histórico: $e';
      items = ObservableList.of([]);
    } finally {
      isLoading = false;
    }
  }

  @action
  Future<HistoryItem?> getItemById(int id) async {
    try {
      final token = _authStore.accessToken!;
      final response = await _itemService.getItemById(id, token);

      if (response != null) {
        return HistoryItem(
          id: response['id'],
          imagePath: response['image_url'] ?? '',
          description: response['description'] ?? 'Sem descrição',
        );
      }
    } catch (e) {
      errorMessage = 'Erro ao buscar item: $e';
    }
    return null;
  }
}
