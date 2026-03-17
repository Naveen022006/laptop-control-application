import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';
import '../services/api_service.dart';
import '../models/models.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _deviceNameController = TextEditingController();
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _deviceNameController.text = 'My Phone';
  }

  @override
  void dispose() {
    _deviceNameController.dispose();
    super.dispose();
  }

  Future<void> _registerDevice() async {
    if (_deviceNameController.text.isEmpty) {
      _showError('Please enter a device name');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      
      // Generate unique device ID
      const uuid = Uuid();
      final deviceId = 'mobile-${uuid.v4()}';

      // Register device
      final response = await apiService.registerDevice(
        deviceId: deviceId,
        deviceName: _deviceNameController.text,
      );

      if (response.success && response.data != null) {
        // Save token and device info locally
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_token', response.data!.apiToken);
        await prefs.setString('device_id', response.data!.deviceId);

        if (mounted) {
          Navigator.of(context).pushReplacementNamed('/dashboard');
        }
      } else {
        _showError(response.error ?? 'Registration failed');
      }
    } catch (e) {
      _showError('Registration error: $e');
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _showError(String message) {
    setState(() => _errorMessage = message);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Laptop Control'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 40),
            const Icon(Icons.laptop_mac, size: 80, color: Colors.blue),
            const SizedBox(height: 40),
            Text(
              'Welcome to Laptop Control',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 20),
            const Text(
              'Control your laptop from your mobile phone',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 60),
            TextField(
              controller: _deviceNameController,
              decoration: InputDecoration(
                labelText: 'Device Name',
                hintText: 'Enter your phone name',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                prefixIcon: const Icon(Icons.devices),
              ),
            ),
            const SizedBox(height: 30),
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _registerDevice,
              icon: const Icon(Icons.login),
              label: _isLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Get Started'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'A unique registration token will be generated for your phone',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }
}
