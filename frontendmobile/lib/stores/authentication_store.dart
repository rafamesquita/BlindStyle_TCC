import 'package:blindstyle/data/services/authentication_service.dart';
import 'package:mobx/mobx.dart';
import 'package:shared_preferences/shared_preferences.dart';

part 'authentication_store.g.dart';

class AuthenticationStore = _AuthenticationStoreBase with _$AuthenticationStore;

abstract class _AuthenticationStoreBase with Store {
  final AuthenticationService _service;

  _AuthenticationStoreBase(this._service);

  @observable
  String? email;

  @observable
  String? name;

  @observable
  String? accessToken;

  @observable
  String? refreshToken;

  @observable
  bool isLoading = false;

  @observable
  String? errorMessage;

  @observable
  bool isLoggedIn = false;

  @action
  Future<bool> login(String email, String password) async {
    isLoading = true;
    errorMessage = null;

    try {
      final data = await _service.login(email, password);
      accessToken = data['access_token'];
      refreshToken = data['refresh_token'];
      name = data['name'];
      this.email = email;

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', accessToken!);
      await prefs.setString('refresh_token', refreshToken!);
      await prefs.setString('email', email);
      if (name != null) await prefs.setString('name', name!);
      return true;
    } catch (e) {
      errorMessage = e.toString();
      return false;
    } finally {
      isLoading = false;
    }
  }

  @action
  Future<bool> register(String name, String email, String password) async {
    isLoading = true;
    errorMessage = null;

    try {
      await _service.register(name, email, password);
      return true;
    } catch (e) {
      errorMessage = e.toString();
      return false;
    } finally {
      isLoading = false;
    }
  }

  @action
  Future<bool> refreshAccessToken() async {
    if (refreshToken == null) return false;

    try {
      final newAccessToken = await _service.refreshToken(refreshToken!);

      accessToken = newAccessToken;

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', newAccessToken);

      return true;
    } catch (e) {
      await logout();
      return false;
    }
  }

  @action
  Future<void> loadSession() async {
    final prefs = await SharedPreferences.getInstance();

    accessToken = prefs.getString('access_token');
    refreshToken = prefs.getString('refresh_token');
    email = prefs.getString('email');
    name = prefs.getString('name');

    if (refreshToken != null) {
      final ok = await refreshAccessToken();
      isLoggedIn = ok;
    } else {
      isLoggedIn = false;
    }
  }

  @action
  Future<void> logout() async {
    accessToken = null;
    refreshToken = null;
    email = null;
    name = null;

    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
