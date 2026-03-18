class AppConfig {
  static const String apiBaseUrl = 'http://localhost:8000';
  static const String wsBaseUrl = 'ws://localhost:8000';

  static const String appName = 'Laptop Control';
  static const String appVersion = '1.0.0';

  // API Timeouts
  static const int connectTimeout = 30000; // milliseconds
  static const int receiveTimeout = 30000;
  static const int sendTimeout = 30000;

  // WebSocket
  static const int wsReconnectDelay = 5000; // milliseconds
  static const int wsHeartbeatInterval = 30000;
}
