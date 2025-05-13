import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/crypto_signal.dart';
import '../models/pump_alert.dart';

class ApiService {
  static const String baseUrl = 'https://criptosinais.replit.app/api';
  
  // Obter sinais de criptomoedas
  static Future<List<CryptoSignal>> getCryptoSignals() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/crypto-signals'))
          .timeout(Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final signals = (data['signals'] as List)
            .map((signal) => CryptoSignal.fromJson(signal))
            .toList();
        
        return signals;
      } else {
        throw Exception('Falha ao obter sinais de criptomoedas');
      }
    } catch (e) {
      print('Erro ao obter sinais de criptomoedas: $e');
      // Retornar lista vazia em caso de erro para evitar falhas no app
      return [];
    }
  }
  
  // Obter alertas de pump
  static Future<List<PumpAlert>> getPumpAlerts() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/pump-signals'))
          .timeout(Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body) as List;
        final alerts = data.map((alert) => PumpAlert.fromJson(alert)).toList();
        
        return alerts;
      } else {
        throw Exception('Falha ao obter alertas de pump');
      }
    } catch (e) {
      print('Erro ao obter alertas de pump: $e');
      // Retornar lista vazia em caso de erro para evitar falhas no app
      return [];
    }
  }
  
  // Obter histórico de preços de uma moeda específica
  static Future<Map<String, dynamic>> getPriceHistory(String coinId, {int limit = 50}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/price-history/$coinId?limit=$limit')
      ).timeout(Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Falha ao obter histórico de preços');
      }
    } catch (e) {
      print('Erro ao obter histórico de preços: $e');
      // Retornar mapa vazio em caso de erro
      return {
        'coin_id': coinId,
        'history': []
      };
    }
  }
  
  // Obter status geral do mercado
  static Future<Map<String, dynamic>> getMarketStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/market-status')
      ).timeout(Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Falha ao obter status do mercado');
      }
    } catch (e) {
      print('Erro ao obter status do mercado: $e');
      // Retornar dados padrão em caso de erro
      return {
        'market_sentiment': 'NEUTRO',
        'market_cap_change_24h': 0.0,
        'btc_dominance': 0.0,
        'eth_dominance': 0.0,
        'timestamp': DateTime.now().toIso8601String()
      };
    }
  }
  
  // Verificar status da API
  static Future<bool> checkApiStatus() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/status')
      ).timeout(Duration(seconds: 5));
      
      return response.statusCode == 200;
    } catch (e) {
      print('Erro ao verificar status da API: $e');
      return false;
    }
  }
}