import 'dart:convert';
import 'dart:io';
import 'package:blindstyle/data/models/clothing_item.dart';
import 'package:blindstyle/data/models/complete_clothing_item.dart';
import 'package:http/http.dart' as http;
import '../models/clothing_description.dart';

class ItemService {
  final String baseUrl;

  ItemService({required this.baseUrl});

  Future<String> createItem(CompleteClothingItem item, String token) async {
    final uri = Uri.parse('$baseUrl/api/v1/items/create');

    final headers = {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };

    final body = jsonEncode(item.toJson());

    final response = await http.post(uri, headers: headers, body: body);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['message'] ?? 'Item criado com sucesso.';
    } else {
      throw Exception(
        'Erro ao criar item (${response.statusCode}): ${response.body}',
      );
    }
  }

  Future<Map<String, dynamic>> getItemById(
    int id,
    String token, {
    bool allowOthers = false,
  }) async {
    final uri = Uri.parse(
      '$baseUrl/api/v1/items/list/$id?allow_others=$allowOthers',
    );

    final response = await http.get(
      uri,
      headers: {'Authorization': 'Bearer $token', 'accept': 'application/json'},
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception(
        'Erro ao buscar itens do usuário (${response.statusCode}): ${response.body}',
      );
    }
  }

  Future<Map<String, dynamic>> getItemsList({
    required String token,
    int page = 1,
    int size = 10,
    String status = 'active',
  }) async {
    final uri = Uri.parse(
      '$baseUrl/api/v1/items/list-all?page=$page&size=$size&status=$status',
    );

    final response = await http.get(
      uri,
      headers: {'Authorization': 'Bearer $token', 'accept': 'application/json'},
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception(
        'Erro ao buscar itens do usuário (${response.statusCode}): ${response.body}',
      );
    }
  }

  Future<ClothingDescription> updateItem(File file) async {
    final uri = Uri.parse('$baseUrl/api/v1/items/update/1');

    final request = http.MultipartRequest('POST', uri);
    request.files.add(await http.MultipartFile.fromPath('file', file.path));

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return ClothingDescription.fromJson(data);
    } else {
      throw Exception('Erro ao processar imagem (${response.statusCode})');
    }
  }

  Future<ClothingDescription> deleteItem(File file) async {
    final uri = Uri.parse('$baseUrl/api/v1/items/delete/2');

    final request = http.MultipartRequest('POST', uri);
    request.files.add(await http.MultipartFile.fromPath('file', file.path));

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return ClothingDescription.fromJson(data);
    } else {
      throw Exception('Erro ao processar imagem (${response.statusCode})');
    }
  }

  Future<ClothingDescription> updateItemStatus(File file) async {
    final uri = Uri.parse('$baseUrl/api/v1/items/update-status/1/status');

    final request = http.MultipartRequest('POST', uri);
    request.files.add(await http.MultipartFile.fromPath('file', file.path));

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return ClothingDescription.fromJson(data);
    } else {
      throw Exception('Erro ao processar imagem (${response.statusCode})');
    }
  }
}
