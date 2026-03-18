enum DeviceStatus { offline, online, idle }

class Device {
  final String id;
  final String deviceId;
  final String name;
  final String deviceType;
  final String? osType;
  final DeviceStatus status;
  final DateTime lastSeen;
  final bool isActive;
  final DateTime createdAt;

  Device({
    required this.id,
    required this.deviceId,
    required this.name,
    required this.deviceType,
    this.osType,
    required this.status,
    required this.lastSeen,
    required this.isActive,
    required this.createdAt,
  });

  factory Device.fromJson(Map<String, dynamic> json) {
    return Device(
      id: json['id'],
      deviceId: json['device_id'],
      name: json['name'],
      deviceType: json['device_type'],
      osType: json['os_type'],
      status: _parseStatus(json['status']),
      lastSeen: DateTime.parse(json['last_seen']),
      isActive: json['is_active'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  static DeviceStatus _parseStatus(String status) {
    switch (status.toLowerCase()) {
      case 'online':
        return DeviceStatus.online;
      case 'idle':
        return DeviceStatus.idle;
      default:
        return DeviceStatus.offline;
    }
  }

  String get statusText {
    switch (status) {
      case DeviceStatus.online:
        return 'Online';
      case DeviceStatus.idle:
        return 'Idle';
      case DeviceStatus.offline:
        return 'Offline';
    }
  }
}
