class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? error;
  final int? statusCode;

  ApiResponse({
    required this.success,
    this.data,
    this.error,
    this.statusCode,
  });

  factory ApiResponse.success(T data) {
    return ApiResponse(success: true, data: data);
  }

  factory ApiResponse.error(String error, {int? statusCode}) {
    return ApiResponse(success: false, error: error, statusCode: statusCode);
  }
}

class Device {
  final String deviceId;
  final String name;
  final String type;
  final String apiToken;
  final bool isActive;
  final DateTime lastOnline;

  Device({
    required this.deviceId,
    required this.name,
    required this.type,
    required this.apiToken,
    required this.isActive,
    required this.lastOnline,
  });

  factory Device.fromJson(Map<String, dynamic> json) {
    return Device(
      deviceId: json['device_id'] ?? '',
      name: json['device_name'] ?? '',
      type: json['device_type'] ?? '',
      apiToken: json['api_token'] ?? '',
      isActive: json['is_active'] ?? true,
      lastOnline: DateTime.parse(json['last_online'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'device_id': deviceId,
      'device_name': name,
      'device_type': type,
      'api_token': apiToken,
      'is_active': isActive,
      'last_online': lastOnline.toIso8601String(),
    };
  }
}

class Command {
  final int id;
  final String deviceId;
  final String commandName;
  final String status;
  final String? result;
  final String? errorMessage;
  final DateTime createdAt;
  final DateTime? executedAt;

  Command({
    required this.id,
    required this.deviceId,
    required this.commandName,
    required this.status,
    this.result,
    this.errorMessage,
    required this.createdAt,
    this.executedAt,
  });

  factory Command.fromJson(Map<String, dynamic> json) {
    return Command(
      id: json['id'] ?? 0,
      deviceId: json['device_id'] ?? '',
      commandName: json['command_name'] ?? '',
      status: json['status'] ?? 'pending',
      result: json['result'],
      errorMessage: json['error_message'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      executedAt: json['executed_at'] != null ? DateTime.parse(json['executed_at']) : null,
    );
  }
}

class SystemMetrics {
  final int id;
  final String deviceId;
  final int cpuPercent;
  final int memoryPercent;
  final int diskPercent;
  final int? temperature;
  final int? batteryPercent;
  final bool? isCharging;
  final DateTime createdAt;

  SystemMetrics({
    required this.id,
    required this.deviceId,
    required this.cpuPercent,
    required this.memoryPercent,
    required this.diskPercent,
    this.temperature,
    this.batteryPercent,
    this.isCharging,
    required this.createdAt,
  });

  factory SystemMetrics.fromJson(Map<String, dynamic> json) {
    return SystemMetrics(
      id: json['id'] ?? 0,
      deviceId: json['device_id'] ?? '',
      cpuPercent: json['cpu_percent'] ?? 0,
      memoryPercent: json['memory_percent'] ?? 0,
      diskPercent: json['disk_percent'] ?? 0,
      temperature: json['temperature'],
      batteryPercent: json['battery_percent'],
      isCharging: json['is_charging'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
    );
  }
}
