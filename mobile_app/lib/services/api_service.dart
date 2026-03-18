import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/app_config.dart';
import '../models/user.dart';
import '../models/device.dart';
import '../models/command.dart';

class ApiService {
  static const storage = FlutterSecureStorage();
  static const String _tokenKey = 'access_token';

  static Future<String?> getToken() async {
    return await storage.read(key: _tokenKey);
  }

  static Future<void> saveToken(String token) async {
    await storage.write(key: _tokenKey, value: token);
  }

  static Future<void> clearToken() async {
    await storage.delete(key: _tokenKey);
  }

  // ==================== Authentication ====================

  static Future<Map<String, dynamic>> register(
    String username,
    String email,
    String password,
  ) async {
    final url = Uri.parse('${AppConfig.apiBaseUrl}/auth/register');

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'email': email,
        'password': password,
      }),
    ).timeout(const Duration(milliseconds: AppConfig.connectTimeout));

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to register: ${response.body}');
    }
  }

  static Future<Map<String, dynamic>> login(
    String username,
    String password,
  ) async {
    final url = Uri.parse('${AppConfig.apiBaseUrl}/auth/login');

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'password': password,
      }),
    ).timeout(const Duration(milliseconds: AppConfig.connectTimeout));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await saveToken(data['access_token']);
      return data;
    } else {
      throw Exception('Failed to login: ${response.body}');
    }
  }

  // ==================== Devices ====================

  static Future<List<Device>> getDevices() async {
    final url = Uri.parse('${AppConfig.apiBaseUrl}/devices/');
    final token = await getToken();

    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    ).timeout(const Duration(milliseconds: AppConfig.connectTimeout));

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Device.fromJson(json)).toList();
    } else {
      throw Exception('Failed to get devices: ${response.body}');
    }
  }

  static Future<Device> registerDevice(
    String deviceId,
    String name,
    String deviceType,
    String? osType,
  ) async {
    final url = Uri.parse('${AppConfig.apiBaseUrl}/devices/register');
    final token = await getToken();

    final response = await http.post(
      url,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'device_id': deviceId,
        'name': name,
        'device_type': deviceType,
        'os_type': osType,
      }),
    ).timeout(const Duration(milliseconds: AppConfig.connectTimeout));

    if (response.statusCode == 200) {
      return Device.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to register device: ${response.body}');
    }
  }

  static Future<Device> getDeviceStats(String deviceId) async {
    final url = Uri.parse('${AppConfig.apiBaseUrl}/devices/$deviceId/stats');
    final token = await getToken();

    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    ).timeout(const Duration(milliseconds: AppConfig.connectTimeout));

    if (response.statusCode == 200) {
      return Device.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to get device stats: ${response.body}');
    }
  }

  // ==================== Commands ====================

  static Future<Command> sendCommand(
    String deviceId,
    String commandType,
    Map<String, dynamic>? parameters,
  ) async {
    final url = Uri.parse('${AppConfig.apiBaseUrl}/commands/');
    final token = await getToken();

    final response = await http.post(
      url,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'device_id': deviceId,
        'command_type': commandType,
        'parameters': parameters,
      }),
    ).timeout(const Duration(milliseconds: AppConfig.connectTimeout));

    if (response.statusCode == 200) {
      return Command.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to send command: ${response.body}');
    }
  }

  static Future<Command> getCommandStatus(String commandId) async {
    final url = Uri.parse('${AppConfig.apiBaseUrl}/commands/$commandId');
    final token = await getToken();

    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    ).timeout(const Duration(milliseconds: AppConfig.connectTimeout));

    if (response.statusCode == 200) {
      return Command.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to get command status: ${response.body}');
    }
  }

  static Future<List<Command>> getCommandHistory(
    String deviceId, {
    int limit = 100,
  }) async {
    final url = Uri.parse(
      '${AppConfig.apiBaseUrl}/commands/device/$deviceId/history?limit=$limit',
    );
    final token = await getToken();

    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    ).timeout(const Duration(milliseconds: AppConfig.connectTimeout));

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Command.fromJson(json)).toList();
    } else {
      throw Exception('Failed to get command history: ${response.body}');
    }
  }
}
