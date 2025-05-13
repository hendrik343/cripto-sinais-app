import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/crypto_signal.dart';
import '../models/pump_alert.dart';
import '../widgets/crypto_card.dart';
import '../services/notification_service.dart';
import 'profile_screen.dart';
import 'pump_alerts_screen.dart';

class DashboardScreen extends StatefulWidget {
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  List<CryptoSignal> cryptoSignals = [];
  List<PumpAlert> pumpAlerts = [];
  bool isLoading = true;
  Timer? refreshTimer;
  bool hasApiError = false;

  @override
  void initState() {
    super.initState();
    // Inicializar serviço de notificações FCM
    NotificationService.initializeFCM();
    
    // Inscrever-se nos tópicos de notificação
    _subscribeToNotificationTopics();
    
    // Carregar dados
    fetchData();
    fetchPumpSignals();
    
    // Configurar atualizações periódicas a cada 30 segundos
    refreshTimer = Timer.periodic(Duration(seconds: 30), (timer) {
      fetchData();
      fetchPumpSignals();
    });
  }
  
  // Inscrever-se nos tópicos de notificação para receber alertas específicos
  Future<void> _subscribeToNotificationTopics() async {
    try {
      // Tópico para todos os alertas de pump
      await NotificationService.subscribeToTopic('pump_alerts');
      
      // Tópicos de moedas específicas
      final commonCoins = ['bitcoin', 'ethereum', 'solana', 'doge', 'floki', 'shib'];
      for (final coin in commonCoins) {
        await NotificationService.subscribeToTopic('coin_$coin');
      }
    } catch (e) {
      print('Erro ao assinar tópicos de notificação: $e');
    }
  }

  @override
  void dispose() {
    refreshTimer?.cancel();
    super.dispose();
  }

  Future<void> fetchData() async {
    try {
      setState(() {
        isLoading = true;
        hasApiError = false;
      });

      // URL base que aponta para a API Flask 
      final String apiUrl = 'https://criptosinais.replit.app/api/crypto-signals';

      final response = await http.get(Uri.parse(apiUrl))
          .timeout(Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        setState(() {
          cryptoSignals = (data['signals'] as List)
              .map((signal) => CryptoSignal.fromJson(signal))
              .toList();
          isLoading = false;
        });
      } else {
        setState(() {
          isLoading = false;
          hasApiError = true;
        });
      }
    } catch (e) {
      setState(() {
        isLoading = false;
        hasApiError = true;
      });
      print('Erro ao carregar dados: $e');
      
      // Dados de fallback para demo
      setState(() {
        cryptoSignals = [
          CryptoSignal(
            coinId: 'bitcoin',
            symbol: 'BTC',
            price: 45000.0,
            percentChange: 2.5,
            recommendation: 'COMPRA',
          ),
          CryptoSignal(
            coinId: 'ethereum',
            symbol: 'ETH',
            price: 3200.0,
            percentChange: 1.8,
            recommendation: 'AGUARDA',
          ),
          CryptoSignal(
            coinId: 'solana',
            symbol: 'SOL',
            price: 175.73,
            percentChange: -0.01,
            recommendation: 'AGUARDA',
          ),
          CryptoSignal(
            coinId: 'dogecoin',
            symbol: 'DOGE',
            price: 0.24786,
            percentChange: -0.00,
            recommendation: 'AGUARDA',
          ),
          CryptoSignal(
            coinId: 'shiba-inu',
            symbol: 'SHIB',
            price: 0.00001728,
            percentChange: 0.00,
            recommendation: 'AGUARDA',
          ),
          CryptoSignal(
            coinId: 'floki',
            symbol: 'FLOKI',
            price: 0.00012071,
            percentChange: -0.29,
            recommendation: 'COMPRA',
          ),
        ];
      });
    }
  }

  Future<void> fetchPumpSignals() async {
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
        pumpAlerts = jsonData.map((data) => PumpAlert.fromJson(data)).toList();
      });
    } catch (e) {
      print('Erro ao carregar alertas de pump: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text('CriptoSinais Dashboard'),
        actions: [
          IconButton(
            icon: Icon(Icons.notifications),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => PumpAlertsScreen()),
              );
            },
          ),
          IconButton(
            icon: Icon(Icons.person),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => ProfileScreen()),
              );
            },
          ),
        ],
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
          onRefresh: () async {
            await fetchData();
            await fetchPumpSignals();
          },
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Alerta de pump, se houver
              if (pumpAlerts.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
                  child: GestureDetector(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => PumpAlertsScreen()),
                      );
                    },
                    child: Container(
                      padding: EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.orange.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: Colors.orange.withOpacity(0.5),
                          width: 1,
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.rocket_launch,
                            color: Colors.orange,
                          ),
                          SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Alerta de PUMP! 🚀',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.orange,
                                  ),
                                ),
                                SizedBox(height: 4),
                                Text(
                                  '${pumpAlerts.length} moeda(s) com potencial de alta. Toque para ver detalhes.',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey.shade300,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Icon(
                            Icons.arrow_forward_ios,
                            size: 16,
                            color: Colors.grey,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),

              // Card com estatísticas do mercado
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Container(
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade900.withOpacity(0.8),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: Colors.indigo.withOpacity(0.3),
                      width: 1,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Mercado Cripto',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Container(
                            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: Colors.green.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Row(
                              children: [
                                Container(
                                  width: 6,
                                  height: 6,
                                  decoration: BoxDecoration(
                                    color: Colors.green,
                                    shape: BoxShape.circle,
                                  ),
                                ),
                                SizedBox(width: 4),
                                Text(
                                  'Online',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.green,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          _buildStatItem(
                            Icons.trending_up,
                            'Alta',
                            '${cryptoSignals.where((s) => s.percentChange > 0).length}',
                            Colors.green,
                          ),
                          _buildStatItem(
                            Icons.trending_down,
                            'Baixa',
                            '${cryptoSignals.where((s) => s.percentChange < 0).length}',
                            Colors.red,
                          ),
                          _buildStatItem(
                            Icons.shopping_cart,
                            'Comprar',
                            '${cryptoSignals.where((s) => s.recommendation == 'COMPRA').length}',
                            Colors.amber,
                          ),
                          _buildStatItem(
                            Icons.sell,
                            'Vender',
                            '${cryptoSignals.where((s) => s.recommendation == 'VENDA').length}',
                            Colors.blue,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),

              // Área principal com lista de sinais
              Expanded(
                child: isLoading
                    ? Center(child: CircularProgressIndicator())
                    : hasApiError
                        ? _buildErrorState()
                        : cryptoSignals.isEmpty
                            ? Center(
                                child: Text(
                                  'Nenhum sinal disponível no momento',
                                  style: TextStyle(color: Colors.grey),
                                ),
                              )
                            : ListView.builder(
                                padding: EdgeInsets.symmetric(horizontal: 16),
                                itemCount: cryptoSignals.length,
                                itemBuilder: (context, index) {
                                  final signal = cryptoSignals[index];
                                  // Verificar se esta moeda tem um alerta de pump
                                  final hasPumpAlert = pumpAlerts.any((alert) => 
                                    alert.coinId.toLowerCase() == signal.coinId.toLowerCase());
                                    
                                  return CryptoCard(
                                    signal: signal,
                                    // Adicionar um indicador visual se houver alerta de pump
                                    // Isso seria implementado no widget CryptoCard
                                  );
                                },
                              ),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          await fetchData();
          await fetchPumpSignals();
        },
        child: Icon(Icons.refresh),
        tooltip: 'Atualizar sinais',
      ),
    );
  }

  Widget _buildStatItem(IconData icon, String label, String value, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey,
          ),
        ),
      ],
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.cloud_off,
              size: 64,
              color: Colors.grey,
            ),
            SizedBox(height: 16),
            Text(
              'Não foi possível conectar à API',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 8),
            Text(
              'Verifique sua conexão com a internet e tente novamente',
              style: TextStyle(
                color: Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: () async {
                await fetchData();
                await fetchPumpSignals();
              },
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.refresh),
                  SizedBox(width: 8),
                  Text('Tentar novamente'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}