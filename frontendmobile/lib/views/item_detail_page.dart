import 'dart:convert';

import 'package:blindstyle/data/models/clothing_item.dart';
import 'package:blindstyle/data/models/complete_clothing_item.dart';
import 'package:blindstyle/data/services/description_service.dart';
import 'package:blindstyle/di/service_locator.dart';
import 'package:blindstyle/stores/accessibility_store.dart';
import 'package:blindstyle/stores/authentication_store.dart';
import 'package:blindstyle/stores/history_store.dart';
import 'package:blindstyle/stores/suggestion_store.dart';
import 'package:blindstyle/themes/high_contrast_theme.dart';
import 'package:blindstyle/widgets/carousel.dart';
import 'package:flutter/material.dart';
import 'package:flutter_mobx/flutter_mobx.dart';

class ItemDetailPage extends StatefulWidget {
  final HistoryItem item;

  const ItemDetailPage({super.key, required this.item});

  @override
  State<ItemDetailPage> createState() => _ItemDetailPageState();
}

class _ItemDetailPageState extends State<ItemDetailPage> {
  final suggestionStore = getIt<SuggestionStore>();
  final accessibilityStore = getIt<AccessibilityStore>();

  bool generated = false;

  @override
  Widget build(BuildContext context) {
    final base64Str =
        widget.item.imagePath.contains(',')
            ? widget.item.imagePath.split(',').last
            : widget.item.imagePath;

    final imageBytes = base64Decode(base64Str);

    return Scaffold(
      appBar: AppBar(
        title: const Text("Detalhes"),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Observer(
        builder: (_) {
          final loading = suggestionStore.isLoading;
          final outfits = suggestionStore.suggestions;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Image.memory(
                    imageBytes,
                    width: 220,
                    height: 220,
                    fit: BoxFit.contain,
                  ),
                ),

                const SizedBox(height: 16),

                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Text(
                      widget.item.description,
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(),
                    ),
                  ),
                ),

                const SizedBox(height: 24),

                if (!generated && !loading)
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color.fromARGB(255, 27, 76, 115),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      onPressed: () async {
                        generated = true;
                        setState(() {});
                        await suggestionStore.generateSuggestions(
                          widget.item.id,
                        );
                      },
                      icon: const Icon(Icons.shuffle, color: Colors.white),
                      label: Text(
                        "Gerar combinações",
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 16 * accessibilityStore.fontSizeFactor,
                        ),
                      ),
                    ),
                  ),

                if (loading)
                  const Column(
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(height: 12),
                      Text("Gerando combinações..."),
                    ],
                  ),

                const SizedBox(height: 16),

                if (!loading && generated)
                  ListView(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    children:
                        outfits.map((outfit) {
                          final images =
                              outfit.pieces.map((p) => p.base64).toList();

                          return GestureDetector(
                            onTap: () {
                              _openPieceDetails(
                                images.first,
                              );
                            },
                            child: Padding(
                              padding: const EdgeInsets.only(bottom: 16),
                              child: Carousel(
                                imagesBase64: images,
                                onImageTap:
                                    (imageBase64) =>
                                        _openPieceDetails(imageBase64),
                              ),
                            ),
                          );
                        }).toList(),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  void _openPieceDetails(String base64Image) async {
    final descService = getIt<DescriptionService>();

    String? description;

    try {
      description = "";
    } catch (_) {
      description = "Não foi possível obter a descrição.";
    }

    if (!mounted) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      useSafeArea: false,
      constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width),
      builder: (_) {
        return DraggableScrollableSheet(
          expand: false,
          initialChildSize: 0.75,
          minChildSize: 0.55,
          maxChildSize: 0.95,
          builder: (context, controller) {
            return Container(
              width: double.infinity,
              decoration: const BoxDecoration(
                borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
              ),
              child: ListView(
                controller: controller,
                padding: const EdgeInsets.all(24),
                children: [
                  Align(
                    alignment: Alignment.centerRight,
                    child: IconButton(
                      icon: const Icon(Icons.close, size: 28),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ),

                  Image.memory(
                    base64Decode(
                      base64Image.contains(',')
                          ? base64Image.split(',').last
                          : base64Image,
                    ),
                    width: double.infinity,
                    height: 260,
                    fit: BoxFit.contain,
                  ),

                  const SizedBox(height: 20),

                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(
                      description ?? "",
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 16),
                    ),
                  ),

                  const SizedBox(height: 30),
                ],
              ),
            );
          },
        );
      },
    );
  }
}
