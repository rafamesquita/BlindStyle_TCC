import 'package:blindstyle/views/item_detail_page.dart';
import 'package:flutter/material.dart';
import 'package:flutter_mobx/flutter_mobx.dart';
import 'package:blindstyle/di/service_locator.dart';
import 'package:blindstyle/stores/history_store.dart';
import 'package:blindstyle/stores/item_store.dart';
import 'package:blindstyle/stores/accessibility_store.dart';
import 'dart:convert';
import '../widgets/bottom_sheet.dart' as BottomSheetDetails;

class HistoryView extends StatefulWidget {
  const HistoryView({super.key});

  @override
  State<HistoryView> createState() => _HistoryViewState();
}

class _HistoryViewState extends State<HistoryView> {
  final historyStore = getIt<HistoryStore>();
  final itemStore = getIt<ItemStore>();
  final accessibilityStore = getIt<AccessibilityStore>();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      historyStore.loadUserItems();
    });
  }

  TextStyle? _scaledTextStyle(TextStyle? baseStyle) {
    if (baseStyle == null) return null;
    return baseStyle.copyWith(
      fontSize: (baseStyle.fontSize ?? 14) * accessibilityStore.fontSizeFactor,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Observer(
        builder: (_) {
          if (historyStore.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          final items = historyStore.items;

          if (items.isEmpty) {
            return Center(
              child: Observer(
                builder:
                    (_) => Text(
                      'Nenhum item no histórico.',
                      style: _scaledTextStyle(
                        Theme.of(context).textTheme.bodyLarge,
                      ),
                    ),
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: items.length,
            itemBuilder: (context, index) {
              final item = items[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 16),
                child: ListTile(
                  leading:
                      item.imagePath.isNotEmpty
                          ? Image.memory(
                            base64Decode(item.imagePath.split(',').last),
                            width: 50,
                            height: 50,
                            fit: BoxFit.cover,
                            errorBuilder:
                                (_, __, ___) =>
                                    const Icon(Icons.broken_image, size: 40),
                          )
                          : const Icon(Icons.image_not_supported, size: 40),
                  title: Text(
                    item.description,
                    style: _scaledTextStyle(
                      Theme.of(context).textTheme.bodyLarge,
                    ),
                  ),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => ItemDetailPage(item: item),
                      ),
                    );
                  },
                ),
              );
            },
          );
        },
      ),
    );
  }
}
