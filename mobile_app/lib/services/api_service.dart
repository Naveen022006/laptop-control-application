import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/models.dart';

class ApiService {
  final String baseUrl;
  String? _authToken;
  String? _deviceId;

  ApiService({required this.baseUrl});

  // Device Management

  /// Register a new device (mobile app)
  Future<ApiResponse<Device>> registerDevice({
    required String deviceId,
    required String deviceName,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/devices/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'device_id': deviceId,
          'device_name': deviceName,
          'device_type': 'mobile',
        }),
      );

      if (response.statusCode == 201) {
        final device = Device.fromJson(jsonDecode(response.body));
        _authToken = device.apiToken;
        _deviceId = device.deviceId;
        return ApiResponse.success(device);
      } else {
        return ApiResponse.error(
          'Failed to register device',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error('Registration error: $e');
    }
  }

  /// Get device information
  Future<ApiResponse<Device>> getDevice(String deviceId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/devices/$deviceId'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        return ApiResponse.success(Device.fromJson(jsonDecode(response.body)));
      } else {
        return ApiResponse.error(
          'Failed to get device',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error('Get device error: $e');
    }
  }

  // Command Execution

  /// Execute a command on a target device
  Future<ApiResponse<Command>> executeCommand({
    required String targetDeviceId,
    required String commandName,
    Map<String, dynamic>? commandParams,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/commands/execute/$targetDeviceId'),
        headers: _getHeaders(),
        body: jsonEncode({
          'command_name': commandName,
          'command_params': commandParams,
        }),
      );

      if (response.statusCode == 200) {
        return ApiResponse.success(Command.fromJson(jsonDecode(response.body)));
      } else {
        return ApiResponse.error(
          'Failed to execute command',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error('Command execution error: $e');
    }
  }

  /// Get command history for a device
  Future<ApiResponse<List<Command>>> getCommandHistory({
    required String deviceId,
    int limit = 50,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/commands/history/$deviceId?limit=$limit'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        final commands = data.map((cmd) => Command.fromJson(cmd)).toList();
        return ApiResponse.success(commands);
      } else {
        return ApiResponse.error(
          'Failed to get command history',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error('Command history error: $e');
    }
  }

  /// Get specific command details
  Future<ApiResponse<Command>> getCommand(int commandId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/commands/$commandId'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        return ApiResponse.success(Command.fromJson(jsonDecode(response.body)));
      } else {
        return ApiResponse.error(
          'Failed to get command',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error('Get command error: $e');
    }
  }

  // System Metrics

  /// Get latest system metrics for a device
  Future<ApiResponse<SystemMetrics>> getLatestMetrics(String deviceId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/metrics/$deviceId/latest'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        return ApiResponse.success(SystemMetrics.fromJson(jsonDecode(response.body)));
      } else {
        return ApiResponse.error(
          'Failed to get metrics',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error('Metrics error: $e');
    }
  }

  /// Get metrics history for a device
  Future<ApiResponse<List<SystemMetrics>>> getMetricsHistory({
    required String deviceId,
    int limit = 100,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/metrics/$deviceId/history?limit=$limit'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        final metrics = data.map((m) => SystemMetrics.fromJson(m)).toList();
        return ApiResponse.success(metrics);
      } else {
        return ApiResponse.error(
          'Failed to get metrics history',
          statusCode: response.statusCode,
        );
      }
    } catch (e) {
      return ApiResponse.error('Metrics history error: $e');
    }
  }

  // Health Check

  /// Check backend health
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // Helper methods

  Map<String, String> _getHeaders() {
    final headers = {'Content-Type': 'application/json'};
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    return headers;
  }

  String? getAuthToken() => _authToken;
  String? getDeviceId() => _deviceId;
  bool isAuthenticated() => _authToken != null;

  void logout() {
    _authToken = null;
    _deviceId = null;
  }
}
