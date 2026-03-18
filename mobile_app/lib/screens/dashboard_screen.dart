import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/device_provider.dart';
import '../models/device.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<DeviceProvider>().fetchDevices();
    });
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
              await context.read<AuthProvider>().logout();
              if (mounted) {
                Navigator.of(context).pushReplacementNamed('/');
              }
            },
          ),
        ],
      ),
      body: Consumer<DeviceProvider>(
        builder: (context, deviceProvider, _) {
          if (deviceProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (deviceProvider.devices.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.devices_other, size: 80, color: Colors.grey),
                  const SizedBox(height: 16),
                  const Text('No devices registered'),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => _showRegisterDialog(context),
                    child: const Text('Register Device'),
                  ),
                ],
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () => deviceProvider.fetchDevices(),
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Your Devices',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.add),
                        onPressed: () => _showRegisterDialog(context),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: deviceProvider.devices.length,
                    itemBuilder: (context, index) {
                      final device = deviceProvider.devices[index];
                      return _buildDeviceCard(context, device, deviceProvider);
                    },
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildDeviceCard(
    BuildContext context,
    Device device,
    DeviceProvider deviceProvider,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: ListTile(
        leading: Icon(
          Icons.laptop,
          color: device.status == DeviceStatus.online
              ? Colors.green
              : Colors.grey,
        ),
        title: Text(device.name),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Status: ${device.statusText}'),
            Text('OS: ${device.osType ?? "Unknown"}'),
          ],
        ),
        trailing: device.status == DeviceStatus.online
            ? const Icon(Icons.check_circle, color: Colors.green)
            : const Icon(Icons.cancel, color: Colors.grey),
        onTap: () => _showDeviceActions(context, device, deviceProvider),
      ),
    );
  }

  void _showDeviceActions(
    BuildContext context,
    Device device,
    DeviceProvider deviceProvider,
  ) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                device.name,
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 24),
              _CommandButton(
                icon: Icons.language,
                label: 'Open Chrome',
                onPressed: device.status == DeviceStatus.online
                    ? () async {
                        Navigator.pop(context);
                        await deviceProvider.sendCommand('open_chrome', null);
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Command sent')),
                          );
                        }
                      }
                    : null,
              ),
              _CommandButton(
                icon: Icons.mail,
                label: 'Open WhatsApp Web',
                onPressed: device.status == DeviceStatus.online
                    ? () async {
                        Navigator.pop(context);
                        await deviceProvider.sendCommand('open_whatsapp_web', null);
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Command sent')),
                          );
                        }
                      }
                    : null,
              ),
              _CommandButton(
                icon: Icons.screenshot,
                label: 'Take Screenshot',
                onPressed: device.status == DeviceStatus.online
                    ? () async {
                        Navigator.pop(context);
                        await deviceProvider.sendCommand('take_screenshot', null);
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Screenshot taken')),
                          );
                        }
                      }
                    : null,
              ),
              _CommandButton(
                icon: Icons.info,
                label: 'System Info',
                onPressed: device.status == DeviceStatus.online
                    ? () async {
                        Navigator.pop(context);
                        await deviceProvider.sendCommand('system_info', null);
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('System info retrieved')),
                          );
                        }
                      }
                    : null,
              ),
              _CommandButton(
                icon: Icons.lock,
                label: 'Lock Screen',
                onPressed: device.status == DeviceStatus.online
                    ? () async {
                        Navigator.pop(context);
                        await deviceProvider.sendCommand('lock_screen', null);
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Screen locked')),
                          );
                        }
                      }
                    : null,
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showRegisterDialog(BuildContext context) {
    final deviceNameController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Register Device'),
        content: TextField(
          controller: deviceNameController,
          decoration: const InputDecoration(labelText: 'Device Name'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              if (deviceNameController.text.isNotEmpty) {
                await context.read<DeviceProvider>().registerDevice(
                      'device-${DateTime.now().millisecondsSinceEpoch}',
                      deviceNameController.text,
                      'laptop',
                      null,
                    );
                Navigator.pop(context);
              }
            },
            child: const Text('Register'),
          ),
        ],
      ),
    );
  }
}

class _CommandButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onPressed;

  const _CommandButton({
    required this.icon,
    required this.label,
    this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton.icon(
        icon: Icon(icon),
        label: Text(label),
        onPressed: onPressed,
      ),
    );
  }
}
