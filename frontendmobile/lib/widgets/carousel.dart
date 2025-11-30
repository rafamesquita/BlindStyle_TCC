import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';

class Carousel extends StatelessWidget {
  final List<String> imagesBase64;
  final void Function(String base64)? onImageTap;

  const Carousel({super.key, required this.imagesBase64, this.onImageTap});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 260, 
      child: PageView.builder(
        controller: PageController(viewportFraction: 0.82),
        itemCount: imagesBase64.length,
        itemBuilder: (context, index) {
          final raw = imagesBase64[index];
          final cleaned = raw.contains(',') ? raw.split(',').last : raw;

          Uint8List? bytes;
          try {
            bytes = base64Decode(cleaned);
          } catch (_) {}

          return GestureDetector(
            onTap: () => onImageTap?.call(raw),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 6),
              child: Card(
                elevation: 4,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(12), 
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      color: Colors.white,
                      child:
                          bytes != null
                              ? Image.memory(
                                bytes,
                                fit: BoxFit.contain, 
                                width: double.infinity,
                                height: double.infinity,
                              )
                              : const Center(
                                child: Icon(
                                  Icons.image_not_supported,
                                  size: 40,
                                  color: Colors.grey,
                                ),
                              ),
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
