import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';

class ClothingBottomSheet extends StatelessWidget {
  final String imageBase64;
  final String? description;

  const ClothingBottomSheet({
    super.key,
    required this.imageBase64,
    this.description,
  });

  @override
  Widget build(BuildContext context) {
    Uint8List? bytes;

    try {
      final cleaned =
          imageBase64.contains(',') ? imageBase64.split(',').last : imageBase64;
      bytes = base64Decode(cleaned);
    } catch (_) {}

    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.65, 
      minChildSize: 0.5,
      maxChildSize: 0.95, 
      builder: (context, controller) {
        return Container(
          decoration: const BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(22)),
          ),
          child: ListView(
            controller: controller,
            padding: const EdgeInsets.all(20),
            children: [
              Align(
                alignment: Alignment.centerRight,
                child: IconButton(
                  icon: const Icon(Icons.close, size: 28),
                  onPressed: () => Navigator.pop(context),
                ),
              ),
              ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child:
                    bytes != null
                        ? Image.memory(
                          bytes,
                          height: 260,
                          width: double.infinity,
                          fit: BoxFit.contain, 
                        )
                        : const Icon(Icons.image_not_supported, size: 120),
              ),

              const SizedBox(height: 20),

              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(
                    description ??
                        "Nenhuma descrição disponível para esta peça.",
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 16),
                  ),
                ),
              ),

              const SizedBox(height: 30),
            ],
          ),
        );
      },
    );
  }
}
