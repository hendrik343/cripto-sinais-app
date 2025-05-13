# CriptoSinais - Aplicativo Flutter de Monitoramento de Criptomoedas

## Descrição
CriptoSinais é um aplicativo móvel desenvolvido com Flutter para monitoramento de criptomoedas em tempo real, fornecendo alertas de pump, análises técnicas e recomendações de compra/venda.

## Funcionalidades Principais

- **Monitoramento em Tempo Real**: Acompanhe os preços de Bitcoin, Ethereum, Solana, Dogecoin, Shiba Inu, Floki, e outras criptomoedas populares.
- **Alertas de Pump**: Receba notificações quando uma moeda apresentar condições favoráveis para valorização baseadas em análise de RSI e volume.
- **Análise Técnica**: Visualize indicadores como RSI (Índice de Força Relativa) e dados de volume.
- **Área Premium (VIP)**: Acesso a recursos exclusivos e análises avançadas mediante pagamento único.
- **Notificações Push**: Alertas em tempo real via Firebase Cloud Messaging sobre movimentos significativos do mercado.
- **Configurações Personalizadas**: Selecione suas moedas favoritas e customize os tipos de alertas que deseja receber.
- **Interface Moderna**: Design elegante com tema escuro e elementos visuais inspirados em interfaces futuristas.

## Tecnologias Utilizadas

- Flutter para desenvolvimento multiplataforma
- Firebase Authentication para gerenciamento de usuários
- Firebase Cloud Messaging para notificações push
- Cloud Firestore para armazenamento de dados
- Stripe para processamento de pagamentos
- API REST para comunicação com o backend em Flask
- Arquitetura modular com separação clara de responsabilidades

## Requisitos de Sistema

- Flutter 3.0 ou superior
- iOS 12.0+ / Android 6.0+
- Dispositivo com conexão à internet

## Como Compilar

1. Certifique-se de ter o Flutter SDK instalado (https://flutter.dev/docs/get-started/install)
2. Clone este repositório
3. Configure suas chaves de Firebase criando um projeto no [Firebase Console](https://console.firebase.google.com/)
4. Adicione o arquivo `google-services.json` na pasta `/android/app`
5. Execute os seguintes comandos:

```bash
flutter pub get
flutter build apk --release
```

O APK compilado estará disponível em:
`build/app/outputs/flutter-apk/app-release.apk`

## Configuração do Firebase

Para o funcionamento completo, você precisa configurar:

1. Firebase Authentication (habilitando e-mail/senha)
2. Firebase Cloud Messaging para notificações
3. Cloud Firestore para armazenamento de dados
4. Firebase Storage (opcional, para armazenamento de imagens)

## Estrutura do Projeto

- `lib/models/`: Modelos de dados como CryptoSignal e PumpAlert
- `lib/screens/`: Telas do aplicativo (Dashboard, Login, Perfil, etc.)
- `lib/services/`: Serviços para comunicação com APIs e Firebase
- `lib/widgets/`: Componentes reutilizáveis da interface
- `lib/main.dart`: Ponto de entrada do aplicativo

## Licença

Este software é proprietário e seu uso é restrito conforme os termos estabelecidos.

---

Desenvolvido com 💙 usando Flutter.