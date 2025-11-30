import 'dart:io';
import 'package:blindstyle/di/service_locator.dart';
import 'package:blindstyle/navigation/app_navigator.dart';
import 'package:blindstyle/navigation/routes.dart';
import 'package:blindstyle/stores/accessibility_store.dart';
import 'package:blindstyle/stores/image_store.dart';
import 'package:blindstyle/stores/item_store.dart';
import 'package:blindstyle/stores/navigation_store.dart';
import 'package:blindstyle/themes/colors.dart';
import 'package:flutter/material.dart';
import 'package:flutter_mobx/flutter_mobx.dart';

class CameraView extends StatefulWidget {
  const CameraView({super.key});

  @override
  State<CameraView> createState() => _CameraViewState();
}

class _CameraViewState extends State<CameraView> {
  final imageStore = getIt<ImageStore>();
  final accessibilityStore = getIt<AccessibilityStore>();
  final itemStore = getIt<ItemStore>();

  void _speak(String text) {
    accessibilityStore.speak(text);
  }

  void _onSave() async {
    final image = imageStore.imageFile;
    final desc = imageStore.description;

    if (image == null || desc == null || desc.isEmpty) {
      _speak('Não há imagem ou descrição para salvar.');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Selecione uma imagem antes de salvar.')),
      );
      return;
    }

    _speak('Salvando imagem e descrição...');
    try {
      final success = await itemStore.saveItem(File(image.path), desc);

      if (success) {
        _speak('Item salvo com sucesso.');

        final navStore = NavigationStore();
        navStore.setPage(AppPage.history);

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const AppNavigator()),
        );
      } else {
        _speak('Não foi possível salvar o item. Tente novamente.');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(itemStore.errorMessage ?? 'Erro desconhecido'),
          ),
        );
      }
    } catch (e) {
      _speak('Erro ao salvar o item.');
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Erro: $e')));
    }
  }

  TextStyle? _scaledTextStyle(TextStyle? baseStyle) {
    if (baseStyle == null) return null;
    return baseStyle.copyWith(
      fontSize: (baseStyle.fontSize ?? 14) * accessibilityStore.fontSizeFactor,
    );
  }

  @override
  Widget build(BuildContext context) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _speak(
        'Tire uma foto ou envie uma imagem da sua peça de roupa para obter a descrição com suas principais características',
      );
    });

    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Center(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: [
              Observer(
                builder:
                    (_) => Semantics(
                      label: 'Título da tela',
                      child: Text(
                        'Tire uma foto ou envie uma imagem da sua peça de roupa para obter a descrição com suas principais características',
                        style: _scaledTextStyle(
                          Theme.of(context).textTheme.titleLarge,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
              ),
              const SizedBox(height: 16),
              Semantics(
                button: true,
                label: 'Botão abrir câmera',
                hint: 'Pressione para abrir a câmera do dispositivo',
                child: FractionallySizedBox(
                  widthFactor: 0.8,
                  child: ElevatedButton(
                    onPressed: () {
                      imageStore.pickFromCamera();
                      _speak('Abrindo câmera');
                    },
                    child: Observer(
                      builder:
                          (_) => Text(
                            'Abrir Câmera',
                            style: _scaledTextStyle(
                              TextStyle(
                                fontSize:
                                    Theme.of(
                                      context,
                                    ).textTheme.labelLarge?.fontSize ??
                                    16,
                                color: Theme.of(context).colorScheme.onPrimary,
                              ),
                            ),
                          ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Semantics(
                button: true,
                label: 'Botão abrir galeria',
                hint: 'Pressione para abrir a galeria de fotos do dispositivo',
                child: FractionallySizedBox(
                  widthFactor: 0.8,
                  child: ElevatedButton(
                    onPressed: () {
                      imageStore.pickFromGallery();
                      _speak('Abrindo galeria');
                    },
                    child: Observer(
                      builder:
                          (_) => Text(
                            'Abrir Galeria',
                            style: _scaledTextStyle(
                              TextStyle(
                                fontSize:
                                    Theme.of(
                                      context,
                                    ).textTheme.labelLarge?.fontSize ??
                                    16,
                                color: Theme.of(context).colorScheme.onPrimary,
                              ),
                            ),
                          ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Observer(
                builder: (_) {
                  final file = imageStore.imageFile;
                  final desc = imageStore.description;

                  if (file == null) return const SizedBox();

                  final descriptionText =
                      (desc == null || desc.isEmpty)
                          ? 'Não foi possível obter a descrição da imagem. Tente novamente.'
                          : desc;

                  return Column(
                    children: [
                      Semantics(
                        label: 'Imagem selecionada',
                        child: Image.file(
                          File(file.path),
                          width: 200,
                          height: 200,
                          fit: BoxFit.cover,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Observer(
                        builder: (_) {
                          if (imageStore.isLoading) {
                            return Column(
                              children: [
                                const SizedBox(height: 12),
                                const CircularProgressIndicator(),
                                const SizedBox(height: 12),
                                Text(
                                  'Analisando imagem...',
                                  style: _scaledTextStyle(
                                    Theme.of(context).textTheme.bodyLarge,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ],
                            );
                          }
                          return Semantics(
                            label: 'Descrição da imagem',
                            child: Text(
                              descriptionText,
                              style: _scaledTextStyle(
                                Theme.of(context).textTheme.bodyLarge,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          );
                        },
                      ),

                      const SizedBox(height: 12),
                      FractionallySizedBox(
                        widthFactor: 0.8,
                        child: ElevatedButton.icon(
                          onPressed: itemStore.isLoading ? null : _onSave,
                          icon: const Icon(Icons.save, color: AppColors.white),
                          label: Observer(
                            builder:
                                (_) => Text(
                                  itemStore.isLoading
                                      ? 'Salvando...'
                                      : 'Salvar Imagem e Descrição',
                                ),
                          ),
                        ),
                      ),
                    ],
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
