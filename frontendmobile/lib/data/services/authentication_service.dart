import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthenticationService {
  final String baseUrl;

  AuthenticationService({required this.baseUrl});

  Future<Map<String, dynamic>> login(String email, String password) async {
    final uri = Uri.parse('$baseUrl/api/v1/users/login');

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else if (response.statusCode == 401) {
      throw Exception('Usuário ou senha inválidos');
    } else {
      throw Exception('Erro ao fazer login (${response.statusCode})');
    }
  }

  Future<void> register(String name, String email, String password) async {
    final uri = Uri.parse('$baseUrl/api/v1/users/register');

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'name': name, 'email': email, 'password': password}),
    );

    if (response.statusCode != 201 && response.statusCode != 200) {
      throw Exception('Erro ao criar conta (${response.statusCode})');
    }
  }

  Future<String> refreshToken(String refreshToken) async {
    final uri = Uri.parse('$baseUrl/api/v1/users/refresh-token');

    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'refresh_token': refreshToken}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['access_token'];
    } else {
      throw Exception('Erro ao atualizar token');
    }
  }
}
