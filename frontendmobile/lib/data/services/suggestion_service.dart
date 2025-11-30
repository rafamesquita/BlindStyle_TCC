import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/clothing_description.dart';

class SuggestionService {
  final String baseUrl;

  SuggestionService({required this.baseUrl});
  Future<Map<String, dynamic>> getSuggestions(int itemId, String token) async {
    final uri = Uri.parse(
      '$baseUrl/api/v1/suggestions/generate?item_id=$itemId',
    );

    final response = await http.post(
      uri,
      headers: {'Authorization': 'Bearer $token', 'accept': 'application/json'},
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception(
        'Erro ao obter sugestões (${response.statusCode}): ${response.body}',
      );
    }
  }
}
