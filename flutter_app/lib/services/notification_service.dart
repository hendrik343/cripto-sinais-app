import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  static final FlutterLocalNotificationsPlugin _flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();
  
  static Future<void> initialize() async {
    // Configuração para Android
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    
    // Configuração para iOS
    const DarwinInitializationSettings initializationSettingsIOS =
        DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    
    // Configuração para todos os dispositivos
    const InitializationSettings initializationSettings =
        InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
    );
    
    await _flutterLocalNotificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: (NotificationResponse response) async {
        // TODO: Navegar para página específica com base na notificação
        print('Notificação clicada: ${response.payload}');
      },
    );
    
    await initializeFCM();
  }
  
  static Future<void> initializeFCM() async {
    FirebaseMessaging messaging = FirebaseMessaging.instance;

    // Solicita permissão (iOS)
    await messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    // Obtém o token do dispositivo
    String? token = await messaging.getToken();
    print("FCM Token: $token");

    // Guarda o token no Firestore
    final user = FirebaseAuth.instance.currentUser;
    if (user != null && token != null) {
      try {
        await FirebaseFirestore.instance
            .collection('users')
            .doc(user.uid)
            .update({'fcm_token': token});
      } catch (e) {
        print('Erro ao salvar token FCM: $e');
      }
    }
    
    // Configura handlers para receber notificações quando o app está em foreground
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Got a message whilst in the foreground!');
      print('Message data: ${message.data}');

      if (message.notification != null) {
        print('Message also contained a notification: ${message.notification}');
        _showLocalNotification(
          title: message.notification?.title ?? 'Nova notificação',
          body: message.notification?.body ?? '',
          payload: message.data.toString(),
        );
      }
    });
    
    // Quando o aplicativo é aberto a partir de uma notificação em segundo plano
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('Aplicativo aberto a partir de notificação: ${message.data}');
      // TODO: Navegar para página específica com base na notificação
    });
  }
  
  static Future<void> _showLocalNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'cripto_sinais_channel',
      'Alertas de Cripto',
      channelDescription: 'Alertas e sinais de criptomoedas',
      importance: Importance.max,
      priority: Priority.high,
      showWhen: true,
    );
    
    const NotificationDetails platformChannelSpecifics =
        NotificationDetails(android: androidPlatformChannelSpecifics);
    
    await _flutterLocalNotificationsPlugin.show(
      0,
      title,
      body,
      platformChannelSpecifics,
      payload: payload,
    );
  }
  
  // Método para enviar notificação de teste (para desenvolvimento)
  static Future<void> sendTestNotification() async {
    await _showLocalNotification(
      title: 'Alerta de PUMP!',
      body: 'FLOKI detectado com potencial de alta. RSI: 27.5, Volume +75%',
      payload: 'pump_alert_floki',
    );
  }
  
  // Método para inscrever em tópicos específicos (ex: moedas específicas)
  static Future<void> subscribeToTopic(String topic) async {
    await FirebaseMessaging.instance.subscribeToTopic(topic);
    print('Inscrito no tópico: $topic');
  }
  
  // Método para desinscrever de tópicos
  static Future<void> unsubscribeFromTopic(String topic) async {
    await FirebaseMessaging.instance.unsubscribeFromTopic(topic);
    print('Desinscrito do tópico: $topic');
  }
}