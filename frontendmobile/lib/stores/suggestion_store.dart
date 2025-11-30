import 'dart:io';

import 'package:blindstyle/data/models/clothing_description.dart';
import 'package:blindstyle/data/models/suggestion_model';
import 'package:blindstyle/data/services/description_service.dart';
import 'package:blindstyle/data/services/suggestion_service.dart';
import 'package:blindstyle/stores/authentication_store.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobx/mobx.dart';

part 'suggestion_store.g.dart';

class SuggestionStore = _SuggestionStoreBase with _$SuggestionStore;

abstract class _SuggestionStoreBase with Store {
  final ImagePicker _picker = ImagePicker();
  final DescriptionService _service;
  final SuggestionService _suggestionService;
  final AuthenticationStore _authStore;

  _SuggestionStoreBase(this._service, this._suggestionService, this._authStore);

  @observable
  XFile? imageFile;

  @observable
  String? description;

  @observable
  ClothingDescription? clothingDescription;

  @observable
  Map<String, dynamic>? analysisResult;

  @observable
  bool isLoading = false;

  @observable
  String? errorMessage;

  @observable
  ObservableList<SuggestedOutfit> suggestions =
      ObservableList<SuggestedOutfit>();

  @action
  Future<void> pickFromCamera() async {
    try {
      final file = await _picker.pickImage(source: ImageSource.camera);
      if (file != null) {
        imageFile = file;
        await _analyze(file);
      }
    } catch (e) {
      errorMessage = 'Erro ao capturar imagem: $e';
    }
  }

  @action
  Future<void> pickFromGallery() async {
    try {
      final file = await _picker.pickImage(source: ImageSource.gallery);
      if (file != null) {
        imageFile = file;
        await _analyze(file);
      }
    } catch (e) {
      errorMessage = 'Erro ao selecionar imagem: $e';
    }
  }

  @action
  Future<void> _analyze(XFile file) async {
    isLoading = true;
    errorMessage = null;
    clothingDescription = null;

    try {
      final result = await _service.getDescription(
        File(file.path),
        _authStore.accessToken!,
      );

      clothingDescription = result;
      description = clothingDescription!.description;
      analysisResult = clothingDescription!.jsonDescription;
    } catch (e) {
      errorMessage = e.toString();
    } finally {
      isLoading = false;
    }
  }

  @action
  Future<void> generateSuggestions(int itemId) async {
    isLoading = true;
    errorMessage = null;
    suggestions.clear();

    try {
      final data = await _suggestionService.getSuggestions(
        itemId,
        _authStore.accessToken!,
      );

      data.forEach((key, value) {
        final outfit = SuggestedOutfit(
          outfitId: value["outfit_id"].toString(),
          pieces:
              (value["pieces"] as List).map((p) {
                return SuggestedPiece(
                  pieceId: p["piece_id"],
                  base64: p["image_base64"],
                );
              }).toList(),
        );

        suggestions.add(outfit);
      });
    } catch (e) {
      errorMessage = e.toString();
    } finally {
      isLoading = false;
    }
  }
}
