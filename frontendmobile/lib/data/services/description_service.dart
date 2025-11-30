import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/clothing_description.dart';

class DescriptionService {
  final String baseUrl;

  DescriptionService({required this.baseUrl});

  Future<ClothingDescription> getDescription(
    File file,
    String authToken,
  ) async {
    final uri = Uri.parse(
      '$baseUrl/api/v1/api/descriptions/extract-features/upload',
    );

    final bytes = await file.readAsBytes();
    final base64Image = base64Encode(bytes);
    final body = jsonEncode({'image_base64': base64Image});

    final response = await http.post(
      uri,
      headers: {
        'Authorization': 'Bearer $authToken',
        'Content-Type': 'application/json',
      },
      body: body,
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return ClothingDescription.fromJson(data);
    } else {
      throw Exception(
        'Erro ao processar imagem (${response.statusCode}): ${response.body}',
      );
    }
  }
}
