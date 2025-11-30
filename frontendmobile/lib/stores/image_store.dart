import 'dart:io';

import 'package:blindstyle/data/models/clothing_description.dart';
import 'package:blindstyle/data/services/description_service.dart';
import 'package:blindstyle/stores/authentication_store.dart';
import 'package:image_picker/image_picker.dart';
import 'package:mobx/mobx.dart';

part 'image_store.g.dart';

class ImageStore = _ImageStoreBase with _$ImageStore;

abstract class _ImageStoreBase with Store {
  final ImagePicker _picker = ImagePicker();
  final DescriptionService _service;
  final AuthenticationStore _authStore;

  _ImageStoreBase(this._service, this._authStore);

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
}
