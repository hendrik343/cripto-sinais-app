import 'package:flutter/material.dart';
import '../services/firebase_service.dart';
import '../services/notification_service.dart';

class SettingsScreen extends StatefulWidget {
  @override
  _SettingsScreenState createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _isLoading = true;
  bool _notificationsEnabled = true;
  List<String> _favoriteCoins = [];
  List<String> _availableCoins = [
    'bitcoin',
    'ethereum',
    'solana',
    'shiba-inu',
    'floki',
    'dogecoin',
    'bonk-token',
    'cardano',
    'chainlink',
    'ripple',
    'avalanche-2',
    'polygon',
    'arbitrum',
    'optimism',
    'render-token',
    'the-graph',
    'aptos',
    'internet-computer',
    'sei-network',
    'starknet'
  ];
  Map<String, String> _coinSymbols = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'solana': 'SOL',
    'shiba-inu': 'SHIB',
    'floki': 'FLOKI',
    'dogecoin': 'DOGE',
    'bonk-token': 'BONK',
    'cardano': 'ADA',
    'chainlink': 'LINK',
    'ripple': 'XRP',
    'avalanche-2': 'AVAX',
    'polygon': 'MATIC',
    'arbitrum': 'ARB',
    'optimism': 'OP',
    'render-token': 'RNDR',
    'the-graph': 'GRT',
    'aptos': 'APT',
    'internet-computer': 'ICP',
    'sei-network': 'SEI',
    'starknet': 'STRK'
  };

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final settings = await FirebaseService.getUserSettings();
      setState(() {
        _notificationsEnabled = settings['notificationsEnabled'] ?? true;
        
        if (settings.containsKey('favoriteCoins')) {
          _favoriteCoins = List<String>.from(settings['favoriteCoins']);
        } else {
          _favoriteCoins = ['bitcoin', 'ethereum', 'solana'];
        }
        
        _isLoading = false;
      });
    } catch (e) {
      print('Erro ao carregar configurações: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _saveSettings() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final settings = {
        'notificationsEnabled': _notificationsEnabled,
        'favoriteCoins': _favoriteCoins,
      };
      
      await FirebaseService.saveUserSettings(settings);
      
      // Atualizar inscrições de notificações
      if (_notificationsEnabled) {
        // Inscrever em tópicos de moedas favoritas
        for (final coin in _favoriteCoins) {
          await FirebaseService.subscribeToTopic('coin_$coin');
        }
        // Inscrever no tópico geral de alertas de pump
        await FirebaseService.subscribeToTopic('pump_alerts');
      } else {
        // Desinscrever de todas as notificações
        for (final coin in _availableCoins) {
          await FirebaseService.unsubscribeFromTopic('coin_$coin');
        }
        await FirebaseService.unsubscribeFromTopic('pump_alerts');
      }
      
      setState(() {
        _isLoading = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Configurações salvas com sucesso')),
      );
    } catch (e) {
      print('Erro ao salvar configurações: $e');
      setState(() {
        _isLoading = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao salvar configurações')),
      );
    }
  }

  void _toggleNotifications(bool value) {
    setState(() {
      _notificationsEnabled = value;
    });
  }

  void _toggleFavoriteCoin(String coinId, bool value) {
    setState(() {
      if (value) {
        if (!_favoriteCoins.contains(coinId)) {
          _favoriteCoins.add(coinId);
        }
      } else {
        _favoriteCoins.remove(coinId);
      }
    });
  }

  Widget _buildFavoriteCoinTile(String coinId) {
    final symbol = _coinSymbols[coinId] ?? coinId.toUpperCase();
    final isFavorite = _favoriteCoins.contains(coinId);
    
    return CheckboxListTile(
      title: Row(
        children: [
          CircleAvatar(
            backgroundColor: Colors.indigo.withOpacity(0.2),
            child: Text(
              symbol.substring(0, 1),
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          SizedBox(width: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                symbol,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                _formatCoinId(coinId),
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey,
                ),
              ),
            ],
          ),
        ],
      ),
      value: isFavorite,
      onChanged: (value) => _toggleFavoriteCoin(coinId, value ?? false),
      activeColor: Colors.indigo,
    );
  }

  String _formatCoinId(String coinId) {
    return coinId
        .split('-')
        .map((word) => word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text('Configurações'),
        actions: [
          IconButton(
            icon: Icon(Icons.info_outline),
            onPressed: () {
              _showAboutDialog();
            },
          ),
        ],
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : Container(
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
              child: ListView(
                padding: EdgeInsets.all(16),
                children: [
                  // Seção de notificações
                  Card(
                    margin: EdgeInsets.only(bottom: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Notificações',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          SizedBox(height: 16),
                          SwitchListTile(
                            title: Text('Ativar notificações push'),
                            subtitle: Text(
                              'Receba alertas de pump e sinais importantes',
                              style: TextStyle(
                                color: Colors.grey,
                                fontSize: 12,
                              ),
                            ),
                            value: _notificationsEnabled,
                            onChanged: _toggleNotifications,
                            secondary: Icon(
                              _notificationsEnabled
                                  ? Icons.notifications_active
                                  : Icons.notifications_off,
                              color: _notificationsEnabled
                                  ? Colors.indigo
                                  : Colors.grey,
                            ),
                            activeColor: Colors.indigo,
                          ),
                          if (_notificationsEnabled)
                            Padding(
                              padding: EdgeInsets.only(
                                left: 16,
                                right: 16,
                                top: 8,
                              ),
                              child: ElevatedButton(
                                onPressed: () async {
                                  await NotificationService.sendTestNotification();
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text(
                                        'Notificação de teste enviada',
                                      ),
                                    ),
                                  );
                                },
                                child: Text('Enviar notificação de teste'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor:
                                      Colors.indigo.withOpacity(0.2),
                                  foregroundColor: Colors.white,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),

                  // Seção de moedas favoritas
                  if (_notificationsEnabled)
                    Card(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Moedas para acompanhar',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            SizedBox(height: 8),
                            Text(
                              'Selecione as criptomoedas que deseja receber alertas',
                              style: TextStyle(
                                color: Colors.grey,
                                fontSize: 12,
                              ),
                            ),
                            SizedBox(height: 16),
                            // Agrupando em uma grade para evitar sobreposição
                            GridView.builder(
                              shrinkWrap: true,
                              physics: NeverScrollableScrollPhysics(),
                              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: 2, // 2 itens por linha
                                childAspectRatio: 3.0, // Ajuste da proporção altura/largura
                                crossAxisSpacing: 10,
                                mainAxisSpacing: 10,
                              ),
                              itemCount: _availableCoins.length,
                              itemBuilder: (context, index) {
                                return _buildFavoriteCoinTile(_availableCoins[index]);
                              },
                            ),
                          ],
                        ),
                      ),
                    ),

                  SizedBox(height: 24),

                  // Botão Salvar
                  ElevatedButton(
                    onPressed: _saveSettings,
                    child: _isLoading
                        ? SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : Text('Salvar configurações'),
                    style: ElevatedButton.styleFrom(
                      minimumSize: Size(double.infinity, 50),
                      backgroundColor: Colors.indigo,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  void _showAboutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Sobre as notificações'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Nosso sistema de notificações usa análise técnica avançada para detectar condições de mercado favoráveis.',
              style: TextStyle(fontSize: 14),
            ),
            SizedBox(height: 16),
            Text(
              'Como funciona:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text('• Análise de RSI em tempo real', style: TextStyle(fontSize: 14)),
            Text('• Monitoramento de volume de negociação', style: TextStyle(fontSize: 14)),
            Text('• Detecção de padrões técnicos', style: TextStyle(fontSize: 14)),
            SizedBox(height: 16),
            Text(
              'Você receberá alertas quando uma moeda mostrar sinais de pump ou condições favoráveis de compra/venda.',
              style: TextStyle(fontSize: 14),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Fechar'),
          ),
        ],
      ),
    );
  }
}