import 'package:firebase_core/firebase_core.dart';

// Este arquivo é gerado automaticamente pelo Firebase CLI quando você configura seu projeto.
// Substitua este conteúdo pelos valores reais obtidos no seu projeto Firebase.

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    // Por padrão, estamos fornecendo opções para Android como exemplo.
    // Em um projeto real, você usaria valores específicos para cada plataforma.
    
    return const FirebaseOptions(
      apiKey: 'YOUR-API-KEY',
      appId: 'YOUR-APP-ID',
      messagingSenderId: 'YOUR-SENDER-ID',
      projectId: 'YOUR-PROJECT-ID',
      authDomain: 'YOUR-AUTH-DOMAIN',
      storageBucket: 'YOUR-STORAGE-BUCKET',
    );
  }
}