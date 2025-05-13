import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import 'package:firebase_auth/firebase_auth.dart';

class PaymentScreen extends StatefulWidget {
  @override
  _PaymentScreenState createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  bool isLoading = false;
  final FirebaseAuth _auth = FirebaseAuth.instance;

  Future<void> _initiatePayment() async {
    setState(() {
      isLoading = true;
    });

    try {
      final user = _auth.currentUser;
      
      if (user == null) {
        _showErrorDialog('É necessário estar logado para ativar o modo VIP.');
        setState(() {
          isLoading = false;
        });
        return;
      }

      // URL da API de pagamento do backend Flask
      // Em produção, este seria o URL real do seu backend
      final apiUrl = 'https://criptosinais.replit.app/create-checkout-session';
      
      // Criar dados do pagamento
      final paymentData = {
        'uid': user.uid,
        'email': user.email,
      };

      // Enviar solicitação para criar sessão de pagamento
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(paymentData),
      ).timeout(Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final String checkoutUrl = data['url'];
        
        // Abrir URL do Stripe no navegador externo
        if (await canLaunchUrl(Uri.parse(checkoutUrl))) {
          await launchUrl(Uri.parse(checkoutUrl), mode: LaunchMode.externalApplication);
        } else {
          _showErrorDialog('Não foi possível abrir a página de pagamento.');
        }
      } else {
        _showErrorDialog('Não foi possível criar a sessão de pagamento.');
      }
    } catch (e) {
      print('Erro ao processar pagamento: $e');
      _showErrorDialog('Erro ao processar pagamento: $e');
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Erro'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: Text('Ativar Plano VIP'),
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
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Cabeçalho VIP
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.amber.shade700.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.amber.shade700,
                    width: 1,
                  ),
                ),
                child: Column(
                  children: [
                    Icon(
                      Icons.star,
                      color: Colors.amber.shade700,
                      size: 50,
                    ),
                    SizedBox(height: 16),
                    Text(
                      'ACESSO VIP PREMIUM',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Colors.amber.shade700,
                      ),
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Plano único - pagamento único',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey,
                      ),
                    ),
                    SizedBox(height: 16),
                    Text(
                      '€4,90',
                      style: TextStyle(
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              
              SizedBox(height: 32),
              
              // Recursos VIP
              Text(
                'Recursos incluídos:',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 16),
              _buildFeatureItem('Análises técnicas avançadas'),
              _buildFeatureItem('Alertas em tempo real'),
              _buildFeatureItem('Sinais de compra/venda prioritários'),
              _buildFeatureItem('Acesso ao grupo VIP do Telegram'),
              _buildFeatureItem('Suporte prioritário'),
              
              Spacer(),
              
              // Botão de pagamento usando o código que você compartilhou
              isLoading
                  ? Center(child: CircularProgressIndicator())
                  : ElevatedButton(
                      onPressed: _initiatePayment,
                      child: Text(
                        'Ativar Acesso VIP',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.black,
                        ),
                      ),
                      style: ElevatedButton.styleFrom(
                        minimumSize: Size(double.infinity, 50),
                        backgroundColor: Colors.amberAccent.shade700,
                        foregroundColor: Colors.black,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
              
              SizedBox(height: 16),
              
              Text(
                'Processamento seguro via Stripe',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFeatureItem(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        children: [
          Icon(
            Icons.check_circle,
            color: Colors.green,
            size: 20,
          ),
          SizedBox(width: 12),
          Text(
            text,
            style: TextStyle(
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
}