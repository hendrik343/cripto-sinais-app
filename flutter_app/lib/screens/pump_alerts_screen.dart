import 'package:flutter/material.dart';
import '../models/pump_alert.dart';
import 'dart:convert';

class PumpAlertsScreen extends StatefulWidget {
  @override
  _PumpAlertsScreenState createState() => _PumpAlertsScreenState();
}

class _PumpAlertsScreenState extends State<PumpAlertsScreen> {
  List<PumpAlert> alerts = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    loadAlerts();
  }

  Future<void> loadAlerts() async {
    setState(() {
      isLoading = true;
    });

    try {
      // Em um caso real, você chamaria sua API para obter os alertas
      // Por exemplo: final response = await apiService.getPumpAlerts();
      
      // Neste exemplo, vamos usar os dados fornecidos
      final jsonString = '''
      [
        {
          "coin": "floki",
          "rsi": 27.5,
          "volume": 14000000.00,
          "avg_volume": 8000000.00,
          "pump_detected": true
        }
      ]
      ''';
      
      final jsonData = json.decode(jsonString) as List;
      
      setState(() {
        alerts = jsonData.map((data) => PumpAlert.fromJson(data)).toList();
        isLoading = false;
      });
    } catch (e) {
      print('Erro ao carregar alertas: $e');
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text('Alertas de Pump'),
        backgroundColor: Colors.black.withOpacity(0.7),
        elevation: 0,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.black,
              Colors.indigo.shade900.withOpacity(0.3),
            ],
          ),
        ),
        child: RefreshIndicator(
          onRefresh: loadAlerts,
          child: isLoading
              ? Center(child: CircularProgressIndicator())
              : alerts.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.notifications_off,
                            size: 64,
                            color: Colors.grey,
                          ),
                          SizedBox(height: 16),
                          Text(
                            'Nenhum alerta de pump no momento',
                            style: TextStyle(
                              fontSize: 18,
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: EdgeInsets.all(16),
                      itemCount: alerts.length,
                      itemBuilder: (context, index) {
                        final alert = alerts[index];
                        return _buildAlertCard(alert);
                      },
                    ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: loadAlerts,
        child: Icon(Icons.refresh),
        tooltip: 'Atualizar alertas',
      ),
    );
  }

  Widget _buildAlertCard(PumpAlert alert) {
    // Cores com base na condição do RSI
    final Color rsiColor = alert.isOversold
        ? Colors.green
        : alert.isOverbought
            ? Colors.red
            : Colors.amber;

    // Ícone com base na condição do alerta
    final IconData alertIcon = alert.pumpDetected
        ? Icons.trending_up
        : Icons.trending_neutral;

    return Card(
      elevation: 4,
      margin: EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: alert.pumpDetected ? Colors.green.withOpacity(0.5) : Colors.transparent,
          width: 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Cabeçalho com ícone e símbolos
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Container(
                      padding: EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: alert.pumpDetected
                            ? Colors.green.withOpacity(0.2)
                            : Colors.grey.withOpacity(0.2),
                      ),
                      child: Icon(
                        alertIcon,
                        color: alert.pumpDetected ? Colors.green : Colors.grey,
                      ),
                    ),
                    SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          alert.symbol,
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          _formatCoinId(alert.coinId),
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: _getRecommendationColor(alert.recommendation).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    alert.recommendation,
                    style: TextStyle(
                      color: _getRecommendationColor(alert.recommendation),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            
            SizedBox(height: 16),
            
            // Indicadores
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildIndicator(
                  'RSI',
                  '${alert.rsi.toStringAsFixed(1)}',
                  rsiColor,
                  _getRsiDescription(alert.rsi),
                ),
                _buildIndicator(
                  'Vol. Atual',
                  '${_formatVolume(alert.volume)}',
                  Colors.blue,
                  'Volume 24h',
                ),
                _buildIndicator(
                  'Vol. Médio',
                  '${_formatVolume(alert.avgVolume)}',
                  Colors.grey,
                  'Média',
                ),
              ],
            ),
            
            SizedBox(height: 16),
            
            // Status e análise
            Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey.shade800.withOpacity(0.3),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Análise Técnica:',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 8),
                  _buildAnalysisText(alert),
                ],
              ),
            ),
            
            SizedBox(height: 12),
            
            // Carimbo de data/hora
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Icon(
                  Icons.access_time,
                  size: 14,
                  color: Colors.grey,
                ),
                SizedBox(width: 4),
                Text(
                  _formatTimestamp(alert.timestamp),
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIndicator(String label, String value, Color color, String description) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey,
          ),
        ),
        SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        SizedBox(height: 2),
        Text(
          description,
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey,
          ),
        ),
      ],
    );
  }

  String _getRsiDescription(double rsi) {
    if (rsi < 30) return 'Sobrevendido';
    if (rsi > 70) return 'Sobrecomprado';
    return 'Neutro';
  }

  Widget _buildAnalysisText(PumpAlert alert) {
    String analysisText = '';

    if (alert.pumpDetected) {
      if (alert.isOversold) {
        analysisText = 'Potencial oportunidade de compra detectada. O RSI está em zona de sobrevenda (${alert.rsi.toStringAsFixed(1)}) e o volume aumentou ${alert.volumeIncreasePercent.toStringAsFixed(0)}% acima da média.';
      } else if (alert.isOverbought) {
        analysisText = 'Possível topo de bombeamento. O RSI está em zona de sobrecompra (${alert.rsi.toStringAsFixed(1)}) com volume ${alert.volumeIncreasePercent.toStringAsFixed(0)}% acima da média.';
      } else {
        analysisText = 'Aumento significativo de volume detectado (${alert.volumeIncreasePercent.toStringAsFixed(0)}% acima da média). Monitorar de perto para possíveis oportunidades.';
      }
    } else {
      analysisText = 'Não há sinais claros de pump neste momento. Continue monitorando.';
    }

    return Text(
      analysisText,
      style: TextStyle(
        fontSize: 13,
        color: Colors.grey.shade300,
      ),
    );
  }

  String _formatCoinId(String coinId) {
    return coinId.split('-').map((word) => word[0].toUpperCase() + word.substring(1)).join(' ');
  }

  String _formatVolume(double volume) {
    if (volume >= 1000000000) {
      return '${(volume / 1000000000).toStringAsFixed(1)}B';
    } else if (volume >= 1000000) {
      return '${(volume / 1000000).toStringAsFixed(1)}M';
    } else if (volume >= 1000) {
      return '${(volume / 1000).toStringAsFixed(1)}K';
    } else {
      return volume.toStringAsFixed(0);
    }
  }

  String _formatTimestamp(DateTime timestamp) {
    return '${timestamp.day}/${timestamp.month}/${timestamp.year} ${timestamp.hour}:${timestamp.minute.toString().padLeft(2, '0')}';
  }

  Color _getRecommendationColor(String recommendation) {
    switch (recommendation) {
      case 'COMPRA':
        return Colors.green;
      case 'VENDA':
        return Colors.red;
      case 'OBSERVAR':
        return Colors.amber;
      case 'AGUARDAR':
      default:
        return Colors.grey;
    }
  }
}