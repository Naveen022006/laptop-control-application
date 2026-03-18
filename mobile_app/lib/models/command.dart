enum CommandStatus { pending, sent, executing, completed, failed, timeout }

class Command {
  final String id;
  final String deviceId;
  final String commandType;
  final CommandStatus status;
  final Map<String, dynamic>? result;
  final String? errorMessage;
  final int? executionTime;
  final DateTime sentAt;
  final DateTime createdAt;

  Command({
    required this.id,
    required this.deviceId,
    required this.commandType,
    required this.status,
    this.result,
    this.errorMessage,
    this.executionTime,
    required this.sentAt,
    required this.createdAt,
  });

  factory Command.fromJson(Map<String, dynamic> json) {
    return Command(
      id: json['id'],
      deviceId: json['device_id'],
      commandType: json['command_type'],
      status: _parseStatus(json['status']),
      result: json['result'],
      errorMessage: json['error_message'],
      executionTime: json['execution_time'],
      sentAt: DateTime.parse(json['sent_at']),
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  static CommandStatus _parseStatus(String status) {
    switch (status.toUpperCase()) {
      case 'PENDING':
        return CommandStatus.pending;
      case 'SENT':
        return CommandStatus.sent;
      case 'EXECUTING':
        return CommandStatus.executing;
      case 'COMPLETED':
        return CommandStatus.completed;
      case 'FAILED':
        return CommandStatus.failed;
      case 'TIMEOUT':
        return CommandStatus.timeout;
      default:
        return CommandStatus.pending;
    }
  }

  String get statusText {
    switch (status) {
      case CommandStatus.pending:
        return 'Pending';
      case CommandStatus.sent:
        return 'Sent';
      case CommandStatus.executing:
        return 'Executing';
      case CommandStatus.completed:
        return 'Completed';
      case CommandStatus.failed:
        return 'Failed';
      case CommandStatus.timeout:
        return 'Timeout';
    }
  }
}
