import 'package:firebase_auth/firebase_auth.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class AuthService {
  static final FirebaseAuth _auth = FirebaseAuth.instance;
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // Realizar login com email e senha
  static Future<User?> signInWithEmailAndPassword(
      String email, String password) async {
    try {
      UserCredential result = await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      return result.user;
    } catch (e) {
      print('Erro de login: $e');
      return null;
    }
  }

  // Registrar um novo usuário
  static Future<User?> registerWithEmailAndPassword(
      String name, String email, String password) async {
    try {
      UserCredential result = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
      
      User? user = result.user;
      
      // Atualizar o nome de exibição do usuário
      if (user != null) {
        await user.updateDisplayName(name);
        
        // Criar um documento no Firestore para o usuário
        await _firestore.collection('users').doc(user.uid).set({
          'name': name,
          'email': email,
          'isVip': false,
          'createdAt': FieldValue.serverTimestamp(),
        });
      }
      
      return user;
    } catch (e) {
      print('Erro de registro: $e');
      return null;
    }
  }

  // Fazer logout
  static Future<void> signOut() async {
    return await _auth.signOut();
  }

  // Obter usuário atual
  static User? getCurrentUser() {
    return _auth.currentUser;
  }

  // Verificar se o usuário está logado
  static bool isUserLoggedIn() {
    return _auth.currentUser != null;
  }

  // Verificar se o usuário é VIP
  static Future<bool> isUserVip() async {
    try {
      User? user = _auth.currentUser;
      
      if (user != null) {
        DocumentSnapshot doc = await _firestore.collection('users').doc(user.uid).get();
        return doc.exists && (doc.data() as Map<String, dynamic>)['isVip'] == true;
      }
      
      return false;
    } catch (e) {
      print('Erro ao verificar status VIP: $e');
      return false;
    }
  }

  // Atualizar status VIP do usuário
  static Future<void> updateVipStatus(bool isVip) async {
    try {
      User? user = _auth.currentUser;
      
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

  // Recuperar senha
  static Future<void> resetPassword(String email) async {
    await _auth.sendPasswordResetEmail(email: email);
  }
}