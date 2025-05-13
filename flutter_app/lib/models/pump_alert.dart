class PumpAlert {
  final String coinId;
  final String symbol;
  final double rsi;
  final double volume;
  final double avgVolume;
  final bool pumpDetected;
  final DateTime timestamp;
  final String recommendation;

  PumpAlert({
    required this.coinId,
    required this.symbol,
    required this.rsi,
    required this.volume,
    required this.avgVolume,
    required this.pumpDetected,
    required this.timestamp,
    required this.recommendation,
  });

  // Getters para cálculos úteis
  double get volumeIncreasePercent => volume > 0 && avgVolume > 0 
    ? ((volume / avgVolume) * 100) - 100 
    : 0;
  
  bool get isOversold => rsi < 30;
  
  bool get isOverbought => rsi > 70;
  
  // Construtor factory para criar um objeto a partir de JSON
  factory PumpAlert.fromJson(Map<String, dynamic> json) {
    // Conversão explícita para evitar erros de tipo
    final coinId = json['coin'] as String? ?? '';
    final symbol = (json['symbol'] as String?) ?? coinId.toUpperCase().substring(0, min(4, coinId.length));
    final rsi = _parseDouble(json['rsi']);
    final volume = _parseDouble(json['volume']);
    final avgVolume = _parseDouble(json['avg_volume']);
    final pumpDetected = json['pump_detected'] as bool? ?? false;
    
    // Determinar a recomendação com base nos indicadores
    String recommendation;
    if (rsi < 30 && pumpDetected) {
      recommendation = 'COMPRA';
    } else if (rsi > 70 && pumpDetected) {
      recommendation = 'VENDA';
    } else if (pumpDetected) {
      recommendation = 'OBSERVAR';
    } else {
      recommendation = 'AGUARDAR';
    }
    
    return PumpAlert(
      coinId: coinId,
      symbol: symbol,
      rsi: rsi,
      volume: volume,
      avgVolume: avgVolume,
      pumpDetected: pumpDetected,
      timestamp: DateTime.now(),
      recommendation: recommendation,
    );
  }
  
  // Converter o objeto para JSON
  Map<String, dynamic> toJson() {
    return {
      'coin': coinId,
      'symbol': symbol,
      'rsi': rsi,
      'volume': volume,
      'avg_volume': avgVolume,
      'pump_detected': pumpDetected,
      'timestamp': timestamp.toIso8601String(),
      'recommendation': recommendation,
    };
  }
  
  // Helper para converter valores para double com segurança
  static double _parseDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is int) return value.toDouble();
    if (value is double) return value;
    if (value is String) {
      try {
        return double.parse(value);
      } catch (e) {
        return 0.0;
      }
    }
    return 0.0;
  }
}

// Helper para garantir o tamanho mínimo
int min(int a, int b) => a < b ? a : b;