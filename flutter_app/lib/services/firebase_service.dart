import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import '../models/pump_alert.dart';

class FirebaseService {
  static final FirebaseAuth _auth = FirebaseAuth.instance;
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  static final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  
  // Autenticação
  static Future<User?> signInWithEmailAndPassword(String email, String password) async {
    try {
      final UserCredential result = await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      return result.user;
    } catch (e) {
      print('Erro no login: $e');
      return null;
    }
  }
  
  static Future<User?> registerWithEmailAndPassword(String email, String password, String name) async {
    try {
      final UserCredential result = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      
      final User? user = result.user;
      
      if (user != null) {
        // Atualizar o nome do usuário
        await user.updateDisplayName(name);
        
        // Criar documento do usuário no Firestore
        await _firestore.collection('users').doc(user.uid).set({
          'name': name,
          'email': email,
          'isVip': false,
          'createdAt': FieldValue.serverTimestamp(),
          'preferences': {
            'notificationsEnabled': true,
            'favoriteCoins': ['bitcoin', 'ethereum', 'solana'],
          },
        });
      }
      
      return user;
    } catch (e) {
      print('Erro no registro: $e');
      return null;
    }
  }
  
  static Future<void> signOut() async {
    return await _auth.signOut();
  }
  
  static User? getCurrentUser() {
    return _auth.currentUser;
  }
  
  static Stream<User?> get userChanges => _auth.userChanges();
  
  // Firestore
  static Future<Map<String, dynamic>?> getUserData() async {
    try {
      final user = _auth.currentUser;
      if (user != null) {
        final doc = await _firestore.collection('users').doc(user.uid).get();
        return doc.data() as Map<String, dynamic>?;
      }
      return null;
    } catch (e) {
      print('Erro ao obter dados do usuário: $e');
      return null;
    }
  }
  
  static Future<bool> isUserVip() async {
    try {
      final userData = await getUserData();
      return userData != null && userData['isVip'] == true;
    } catch (e) {
      print('Erro ao verificar status VIP: $e');
      return false;
    }
  }
  
  static Future<void> updateUserVipStatus(bool isVip) async {
    try {
      final user = _auth.currentUser;
      if (user != null) {
        await _firestore.collection('users').doc(user.uid).update({
          'isVip': isVip,
          'vipUpdatedAt': FieldValue.serverTimestamp(),
        });
      }
    } catch (e) {
      print('Erro ao atualizar status VIP: $e');
    }
  }
  
  // Pump Alerts
  static Future<void> storePumpAlert(PumpAlert alert) async {
    try {
      await _firestore.collection('pump_alerts').add({
        'coinId': alert.coinId,
        'symbol': alert.symbol,
        'rsi': alert.rsi,
        'volume': alert.volume,
        'avgVolume': alert.avgVolume,
        'pumpDetected': alert.pumpDetected,
        'timestamp': FieldValue.serverTimestamp(),
        'recommendation': alert.recommendation,
      });
    } catch (e) {
      print('Erro ao salvar alerta de pump: $e');
    }
  }
  
  static Stream<List<PumpAlert>> getPumpAlertsStream() {
    return _firestore
        .collection('pump_alerts')
        .orderBy('timestamp', descending: true)
        .limit(20)
        .snapshots()
        .map((snapshot) {
          return snapshot.docs.map((doc) {
            final data = doc.data();
            final timestamp = (data['timestamp'] as Timestamp?)?.toDate() ?? DateTime.now();
            
            return PumpAlert(
              coinId: data['coinId'] ?? '',
              symbol: data['symbol'] ?? '',
              rsi: (data['rsi'] as num?)?.toDouble() ?? 0,
              volume: (data['volume'] as num?)?.toDouble() ?? 0,
              avgVolume: (data['avgVolume'] as num?)?.toDouble() ?? 0,
              pumpDetected: data['pumpDetected'] ?? false,
              timestamp: timestamp,
              recommendation: data['recommendation'] ?? 'AGUARDAR',
            );
          }).toList();
        });
  }
  
  // FCM
  static Future<String?> getFCMToken() async {
    return await _messaging.getToken();
  }
  
  static Future<void> subscribeToTopic(String topic) async {
    await _messaging.subscribeToTopic(topic);
  }
  
  static Future<void> unsubscribeFromTopic(String topic) async {
    await _messaging.unsubscribeFromTopic(topic);
  }
  
  static Future<void> saveUserSettings(Map<String, dynamic> settings) async {
    try {
      final user = _auth.currentUser;
      if (user != null) {
        await _firestore.collection('users').doc(user.uid).update({
          'preferences': settings,
        });
      }
    } catch (e) {
      print('Erro ao salvar configurações do usuário: $e');
    }
  }
  
  // Obter configurações do usuário
  static Future<Map<String, dynamic>> getUserSettings() async {
    try {
      final userData = await getUserData();
      if (userData != null && userData.containsKey('preferences')) {
        return userData['preferences'] as Map<String, dynamic>;
      }
      return {
        'notificationsEnabled': true,
        'favoriteCoins': ['bitcoin', 'ethereum', 'solana'],
      };
    } catch (e) {
      print('Erro ao obter configurações do usuário: $e');
      return {
        'notificationsEnabled': true,
        'favoriteCoins': ['bitcoin', 'ethereum', 'solana'],
      };
    }
  }
  
  // Salvar preferências de moedas
  static Future<void> saveFavoriteCoins(List<String> coins) async {
    try {
      final settings = await getUserSettings();
      settings['favoriteCoins'] = coins;
      await saveUserSettings(settings);
    } catch (e) {
      print('Erro ao salvar moedas favoritas: $e');
    }
  }
}