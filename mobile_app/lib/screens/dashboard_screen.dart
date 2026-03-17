import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../models/models.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  late ApiService apiService;
  String? _targetDeviceId = 'laptop-001'; // Would be selected from device list
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    apiService = Provider.of<ApiService>(context, listen: false);
    _loadDeviceInfo();
  }

  Future<void> _loadDeviceInfo() async {
    final prefs = await SharedPreferences.getInstance();
    final deviceId = prefs.getString('device_id');
    // Fetch registered laptops from backend
  }

  Future<void> _executeCommand(String commandName, {Map<String, dynamic>? params}) async {
    if (_targetDeviceId == null) {
      _showError('Please select a laptop');
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await apiService.executeCommand(
        targetDeviceId: _targetDeviceId!,
        commandName: commandName,
        commandParams: params,
      );

      if (response.success) {
        _showSuccess('Command executed: $commandName');
        _checkCommandStatus(response.data!.id);
      } else {
        _showError(response.error ?? 'Command failed');
      }
    } catch (e) {
      _showError('Error: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _checkCommandStatus(int commandId) async {
    for (int i = 0; i < 10; i++) {
      await Future.delayed(const Duration(seconds: 1));

      try {
        final response = await apiService.getCommand(commandId);
        if (response.success) {
          final command = response.data!;
          if (command.status == 'completed' || command.status == 'failed') {
            _showCommandResult(command);
            break;
          }
        }
      } catch (e) {
        // Continue polling
      }
    }
  }

  void _showCommandResult(Command command) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('${command.commandName} - ${command.status}'),
        content: SingleChildScrollView(
          child: Text(
            command.result ?? command.errorMessage ?? 'No response',
            maxLines: 10,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.green),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Laptop Control Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              final prefs = await SharedPreferences.getInstance();
              await prefs.clear();
              if (mounted) {
                Navigator.of(context).pushReplacementNamed('/login');
              }
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Device Selection
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Target Device',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 12),
                    DropdownButton<String>(
                      isExpanded: true,
                      value: _targetDeviceId,
                      items: const [
                        DropdownMenuItem(value: 'laptop-001', child: Text('Laptop 001')),
                      ],
                      onChanged: (value) {
                        setState(() => _targetDeviceId = value);
                      },
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // System Commands
            Text(
              'System Commands',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),

            CommandButton(
              icon: Icons.language,
              label: 'Open Chrome',
              onPressed: _isLoading ? null : () => _executeCommand('open_chrome'),
            ),
            CommandButton(
              icon: Icons.message,
              label: 'Open WhatsApp',
              onPressed: _isLoading ? null : () => _executeCommand('open_whatsapp'),
            ),
            CommandButton(
              icon: Icons.screenshot,
              label: 'Take Screenshot',
              onPressed: _isLoading ? null : () => _executeCommand('take_screenshot'),
            ),
            CommandButton(
              icon: Icons.info,
              label: 'System Info',
              onPressed: _isLoading ? null : () => _executeCommand('system_info'),
            ),

            const SizedBox(height: 24),

            // Dangerous Commands
            Text(
              'System Control',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),

            CommandButton(
              icon: Icons.restart_alt,
              label: 'Restart',
              color: Colors.orange,
              onPressed: _isLoading 
                  ? null 
                  : () => _showConfirmDialog(
                      'Restart System?',
                      'This will restart your laptop',
                      () => _executeCommand('restart'),
                    ),
            ),
            CommandButton(
              icon: Icons.power_settings_new,
              label: 'Shutdown',
              color: Colors.red,
              onPressed: _isLoading 
                  ? null 
                  : () => _showConfirmDialog(
                      'Shutdown System?',
                      'This will shutdown your laptop',
                      () => _executeCommand('shutdown'),
                    ),
            ),
          ],
        ),
      ),
    );
  }

  void _showConfirmDialog(String title, String message, VoidCallback onConfirm) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              onConfirm();
            },
            child: const Text('Confirm'),
          ),
        ],
      ),
    );
  }
}

class CommandButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onPressed;
  final Color color;

  const CommandButton({
    Key? key,
    required this.icon,
    required this.label,
    this.onPressed,
    this.color = Colors.blue,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: ElevatedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon),
        label: Text(label),
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}
