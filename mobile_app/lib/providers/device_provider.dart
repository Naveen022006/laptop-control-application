import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/device.dart';
import '../models/command.dart';

class DeviceProvider extends ChangeNotifier {
  List<Device> _devices = [];
  String? _selectedDeviceId;
  bool _isLoading = false;
  String? _error;
  List<Command> _commandHistory = [];

  List<Device> get devices => _devices;
  Device? get selectedDevice => _selectedDeviceId != null
      ? _devices.firstWhere(
          (d) => d.deviceId == _selectedDeviceId,
          orElse: () => _devices.first,
        )
      : null;
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<Command> get commandHistory => _commandHistory;

  Future<void> fetchDevices() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _devices = await ApiService.getDevices();
      if (_devices.isNotEmpty && _selectedDeviceId == null) {
        _selectedDeviceId = _devices.first.deviceId;
      }
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> registerDevice(
    String deviceId,
    String name,
    String deviceType,
    String? osType,
  ) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final device = await ApiService.registerDevice(
        deviceId,
        name,
        deviceType,
        osType,
      );
      _devices.add(device);
      _selectedDeviceId = device.deviceId;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  void selectDevice(String deviceId) {
    _selectedDeviceId = deviceId;
    notifyListeners();
  }

  Future<bool> sendCommand(
    String commandType,
    Map<String, dynamic>? parameters,
  ) async {
    if (_selectedDeviceId == null) {
      _error = 'No device selected';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await ApiService.sendCommand(
        _selectedDeviceId!,
        commandType,
        parameters,
      );
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> fetchCommandHistory() async {
    if (_selectedDeviceId == null) return;

    try {
      _commandHistory = await ApiService.getCommandHistory(_selectedDeviceId!);
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
