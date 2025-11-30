import 'dart:convert';
import 'dart:io';
import 'package:blindstyle/data/models/complete_clothing_item.dart';
import 'package:blindstyle/data/services/item_service.dart';
import 'package:blindstyle/stores/authentication_store.dart';
import 'package:mobx/mobx.dart';

part 'item_store.g.dart';

class ItemStore = _ItemStoreBase with _$ItemStore;

abstract class _ItemStoreBase with Store {
  final ItemService _itemService;
  final AuthenticationStore _authStore;

  _ItemStoreBase(this._itemService, this._authStore);

  @observable
  bool isLoading = false;

  @observable
  String? errorMessage;

  @observable
  Map<String, dynamic>? lastSavedItem;

  @action
  Future<bool> saveItem(File imageFile, String description) async {
    isLoading = true;
    errorMessage = null;

    try {
      final bytes = await imageFile.readAsBytes();
      final base64Image = base64Encode(bytes);

      final parsed = parseDescriptionToAttributes(description);

      final item = CompleteClothingItem(
        name: "Peça de roupa analisada",
        description: description ?? "teste",
        category: parsed["category"] ?? "tops",
        itemType: parsed["item_type"] ?? "tshirt",
        primaryColor: parsed["primary_color"] ?? "red",
        usage: parsed["usage"] ?? "casual",
        texture: parsed["texture"] ?? "smooth",
        printCategory: parsed["print_category"] ?? "plain",
        imageUrl: base64Image,
        ownership: true,
      );

      final result = await _itemService.createItem(
        item,
        _authStore.accessToken!,
      );
      return true;
    } catch (e) {
      errorMessage = 'Erro ao salvar o item: $e';
      return false;
    } finally {
      isLoading = false;
    }
  }

  Map<String, String?> parseDescriptionToAttributes(String description) {
    final parts = description.split(',');
    final cleaned = parts.map((p) => p.trim().toLowerCase()).toList();

    String? category;
    String? itemType;
    String? primaryColor;
    String? texture;
    String? printCategory;
    String? usage;

    for (final part in cleaned) {
      if (part.contains("tops") ||
          part.contains("camisa") ||
          part.contains("blusa")) {
        category = "tops";
      }

      if (part.contains("tshirt") ||
          part.contains("camiseta") ||
          part.contains("t-shirt")) {
        itemType = "tshirt";
      }

      if (part.contains("cor") || part.contains("color")) {
        primaryColor =
            part.replaceAll("de cor", "").replaceAll("cor", "").trim();
      }

      if (part.contains("textura") || part.contains("tecido")) {
        texture =
            part.replaceAll("com textura", "").replaceAll("textura", "").trim();
      }

      if (part.contains("estampa") || part.contains("print")) {
        printCategory =
            part.replaceAll("estampa", "").replaceAll("print", "").trim();
      }

      if (part.contains("uso") || part.contains("recomendado")) {
        usage =
            part
                .replaceAll("recomendado para uso de", "")
                .replaceAll("uso", "")
                .trim();
      }
    }

    return {
      "category": category,
      "item_type": itemType,
      "primary_color": primaryColor,
      "texture": texture,
      "print_category": printCategory,
      "usage": usage,
    };
  }
}
