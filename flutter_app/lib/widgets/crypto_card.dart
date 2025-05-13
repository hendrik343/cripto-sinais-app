import 'package:flutter/material.dart';
import '../models/crypto_signal.dart';

class CryptoCard extends StatelessWidget {
  final CryptoSignal signal;
  final bool showBadge;
  final VoidCallback? onTap;

  const CryptoCard({
    Key? key,
    required this.signal,
    this.showBadge = false,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      margin: EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: signal.isBuyRecommendation
              ? Colors.green.withOpacity(0.5)
              : signal.isSellRecommendation
                  ? Colors.red.withOpacity(0.5)
                  : Colors.transparent,
          width: signal.isBuyRecommendation || signal.isSellRecommendation ? 1.5 : 0,
        ),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
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
                        padding: EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: Colors.grey.shade800.withOpacity(0.5),
                        ),
                        child: Text(
                          signal.symbol.substring(0, 1),
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      SizedBox(width: 12),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            signal.symbol,
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            _formatCoinId(signal.coinId),
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  if (showBadge && signal.isBuyRecommendation)
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(
                        color: Colors.green.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Text(
                        'COMPRA',
                        style: TextStyle(
                          color: Colors.green,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    )
                  else if (showBadge && signal.isSellRecommendation)
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(
                        color: Colors.red.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Text(
                        'VENDA',
                        style: TextStyle(
                          color: Colors.red,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ),
                ],
              ),
              
              SizedBox(height: 16),
              
              // Preço e variação
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    signal.getFormattedPrice(),
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Row(
                    children: [
                      Icon(
                        signal.isPositiveChange
                            ? Icons.trending_up
                            : signal.isNegativeChange
                                ? Icons.trending_down
                                : Icons.trending_flat,
                        color: signal.isPositiveChange
                            ? Colors.green
                            : signal.isNegativeChange
                                ? Colors.red
                                : Colors.grey,
                        size: 20,
                      ),
                      SizedBox(width: 4),
                      Text(
                        signal.getFormattedPercentChange(),
                        style: TextStyle(
                          color: signal.isPositiveChange
                              ? Colors.green
                              : signal.isNegativeChange
                                  ? Colors.red
                                  : Colors.grey,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              
              SizedBox(height: 12),
              
              // Recomendação
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Sinal:',
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 14,
                    ),
                  ),
                  Container(
                    padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: signal.getRecommendationColor().withOpacity(0.2),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: signal.getRecommendationColor().withOpacity(0.5),
                        width: 1,
                      ),
                    ),
                    child: Text(
                      signal.recommendation,
                      style: TextStyle(
                        color: signal.getRecommendationColor(),
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatCoinId(String coinId) {
    return coinId
        .split('-')
        .map((word) => word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }
}