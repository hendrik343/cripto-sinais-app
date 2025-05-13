import 'package:flutter/material.dart';

class CryptoSignal {
  final String coinId;
  final String symbol;
  final double price;
  final double percentChange;
  final String recommendation;

  CryptoSignal({
    required this.coinId,
    required this.symbol,
    required this.price,
    required this.percentChange,
    required this.recommendation,
  });

  // Construtor factory para criar um objeto a partir de JSON
  factory CryptoSignal.fromJson(Map<String, dynamic> json) {
    // Conversão explícita para evitar erros de tipo
    final coinId = json['coin_id'] as String? ?? '';
    final symbol = (json['symbol'] as String?) ?? coinId.toUpperCase().substring(0, min(4, coinId.length));
    
    // Parsing numérico seguro
    num priceValue = 0.0;
    if (json['price'] is num) {
      priceValue = json['price'];
    } else if (json['price'] is String) {
      priceValue = double.tryParse(json['price'] as String) ?? 0.0;
    }
    
    num percentChangeValue = 0.0;
    if (json['percent_change'] is num) {
      percentChangeValue = json['percent_change'];
    } else if (json['percent_change'] is String) {
      percentChangeValue = double.tryParse(json['percent_change'] as String) ?? 0.0;
    }
    
    final price = priceValue.toDouble();
    final percentChange = percentChangeValue.toDouble();
    final recommendation = json['recommendation'] as String? ?? 'AGUARDA';
    
    return CryptoSignal(
      coinId: coinId,
      symbol: symbol,
      price: price,
      percentChange: percentChange,
      recommendation: recommendation,
    );
  }
  
  // Converter o objeto para JSON
  Map<String, dynamic> toJson() {
    return {
      'coin_id': coinId,
      'symbol': symbol,
      'price': price,
      'percent_change': percentChange,
      'recommendation': recommendation,
    };
  }
  
  // Métodos de conveniência
  bool get isPositiveChange => percentChange > 0;
  bool get isNegativeChange => percentChange < 0;
  bool get isBuyRecommendation => recommendation == 'COMPRA';
  bool get isSellRecommendation => recommendation == 'VENDA';
  bool get isWaitRecommendation => recommendation == 'AGUARDA' || recommendation == 'OBSERVAR';
  
  // Obter a cor correspondente à recomendação
  Color getRecommendationColor() {
    if (recommendation == 'COMPRA') {
      return Colors.green;
    } else if (recommendation == 'VENDA') {
      return Colors.red;
    } else if (recommendation == 'OBSERVAR') {
      return Colors.amber;
    } else {
      return Colors.grey;
    }
  }
  
  // Formatação de preço para exibição
  String getFormattedPrice() {
    if (price < 0.00001) {
      return '\$${price.toStringAsExponential(2)}';
    } else if (price < 0.01) {
      return '\$${price.toStringAsFixed(6)}';
    } else if (price < 1) {
      return '\$${price.toStringAsFixed(4)}';
    } else if (price < 1000) {
      return '\$${price.toStringAsFixed(2)}';
    } else {
      return '\$${price.toStringAsFixed(0)}';
    }
  }
  
  // Formatação de variação percentual
  String getFormattedPercentChange() {
    final prefix = percentChange >= 0 ? '+' : '';
    return '$prefix${percentChange.toStringAsFixed(2)}%';
  }
}

// Helper para garantir o tamanho mínimo
int min(int a, int b) => a < b ? a : b;