import 'package:flutter/material.dart';

enum SignalDirection {
  buy,   // Sinal de compra (verde)
  sell,  // Sinal de venda (vermelho)
  watch, // Sinal para observar (amarelo)
  wait   // Sinal neutro, aguardar (cinza)
}

class SignalIndicator extends StatelessWidget {
  final SignalDirection direction;
  final bool showLabel;
  final double size;
  
  const SignalIndicator({
    Key? key,
    required this.direction,
    this.showLabel = true,
    this.size = 12.0,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: _getColor(),
            boxShadow: [
              BoxShadow(
                color: _getColor().withOpacity(0.5),
                blurRadius: 4,
                spreadRadius: 1,
              ),
            ],
          ),
        ),
        if (showLabel) ...[
          SizedBox(width: 4),
          Text(
            _getLabel(),
            style: TextStyle(
              color: _getColor(),
              fontWeight: FontWeight.bold,
              fontSize: size * 0.9,
            ),
          ),
        ],
      ],
    );
  }
  
  Color _getColor() {
    switch (direction) {
      case SignalDirection.buy:
        return Colors.green;
      case SignalDirection.sell:
        return Colors.red;
      case SignalDirection.watch:
        return Colors.amber;
      case SignalDirection.wait:
        return Colors.grey;
    }
  }
  
  String _getLabel() {
    switch (direction) {
      case SignalDirection.buy:
        return 'COMPRAR';
      case SignalDirection.sell:
        return 'VENDER';
      case SignalDirection.watch:
        return 'OBSERVAR';
      case SignalDirection.wait:
        return 'AGUARDAR';
    }
  }
}

// Widget animado que pulsa quando ativo
class PulsingSignalIndicator extends StatefulWidget {
  final SignalDirection direction;
  final bool isActive;
  final double size;
  
  const PulsingSignalIndicator({
    Key? key,
    required this.direction,
    this.isActive = true,
    this.size = 12.0,
  }) : super(key: key);
  
  @override
  _PulsingSignalIndicatorState createState() => _PulsingSignalIndicatorState();
}

class _PulsingSignalIndicatorState extends State<PulsingSignalIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  
  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: Duration(seconds: 1),
    )..repeat(reverse: true);
    
    _animation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Curves.easeInOut,
      ),
    );
    
    if (!widget.isActive) {
      _controller.stop();
    }
  }
  
  @override
  void didUpdateWidget(PulsingSignalIndicator oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isActive && !oldWidget.isActive) {
      _controller.repeat(reverse: true);
    } else if (!widget.isActive && oldWidget.isActive) {
      _controller.stop();
    }
  }
  
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    Color color = _getColor();
    
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Container(
          width: widget.size,
          height: widget.size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color,
            boxShadow: widget.isActive
                ? [
                    BoxShadow(
                      color: color.withOpacity(0.5 * _animation.value),
                      blurRadius: 6 * _animation.value,
                      spreadRadius: 2 * _animation.value,
                    ),
                  ]
                : null,
          ),
        );
      },
    );
  }
  
  Color _getColor() {
    switch (widget.direction) {
      case SignalDirection.buy:
        return Colors.green;
      case SignalDirection.sell:
        return Colors.red;
      case SignalDirection.watch:
        return Colors.amber;
      case SignalDirection.wait:
        return Colors.grey;
    }
  }
}