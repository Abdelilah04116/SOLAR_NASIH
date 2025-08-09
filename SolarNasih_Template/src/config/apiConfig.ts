// Configuration dynamique des APIs pour différents environnements
export const API_CONFIG = {
  // URLs des services backend
  SMA_API_URL: import.meta.env.VITE_SMA_API_URL || 'http://localhost:8000',
  RAG_API_URL: import.meta.env.VITE_RAG_API_URL || 'http://localhost:8001',
  
  // Configuration de l'application
  APP_NAME: import.meta.env.VITE_APP_NAME || 'SolarNasih',
  APP_VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',
  ENVIRONMENT: import.meta.env.VITE_ENVIRONMENT || 'development',
  
  // Configuration des fonctionnalités
  FEATURES: {
    CHAT: import.meta.env.VITE_ENABLE_CHAT !== 'false',
    FILE_UPLOAD: import.meta.env.VITE_ENABLE_FILE_UPLOAD !== 'false',
    VOICE_INPUT: import.meta.env.VITE_ENABLE_VOICE_INPUT !== 'false',
    IMAGE_ANALYSIS: import.meta.env.VITE_ENABLE_IMAGE_ANALYSIS !== 'false',
  },
  
  // Limites
  LIMITS: {
    MAX_FILE_SIZE: parseInt(import.meta.env.VITE_MAX_FILE_SIZE || '52428800'), // 50MB
    MAX_MESSAGE_LENGTH: parseInt(import.meta.env.VITE_MAX_MESSAGE_LENGTH || '4000'),
    MAX_CONVERSATION_LENGTH: parseInt(import.meta.env.VITE_MAX_CONVERSATION_LENGTH || '50'),
  },
  
  // Endpoints
  ENDPOINTS: {
    SMA: {
      CHAT: '/chat',
      UPLOAD_DOCUMENT: '/upload-document',
      SIMULATE_ENERGY: '/simulate-energy',
      DOCUMENTS: '/documents',
      HEALTH: '/health',
    },
    RAG: {
      UPLOAD_FILE: '/upload/file',
      SEARCH: '/search',
      HEALTH: '/health',
      CHAT: '/chat',
    }
  }
};

// Fonction utilitaire pour construire les URLs complètes
export const buildApiUrl = (service: 'SMA' | 'RAG', endpoint: string): string => {
  const baseUrl = service === 'SMA' ? API_CONFIG.SMA_API_URL : API_CONFIG.RAG_API_URL;
  return `${baseUrl}${endpoint}`;
};

// Validation de la configuration
export const validateConfig = (): boolean => {
  const requiredEnvVars = ['VITE_SMA_API_URL', 'VITE_RAG_API_URL'];
  const missingVars = requiredEnvVars.filter(varName => !import.meta.env[varName]);
  
  if (missingVars.length > 0) {
    console.warn('Variables d\'environnement manquantes:', missingVars);
    return false;
  }
  
  return true;
};

// Log de la configuration en mode développement
if (API_CONFIG.ENVIRONMENT === 'development') {
  console.log('🔧 Configuration API:', {
    SMA_API_URL: API_CONFIG.SMA_API_URL,
    RAG_API_URL: API_CONFIG.RAG_API_URL,
    ENVIRONMENT: API_CONFIG.ENVIRONMENT,
    FEATURES: API_CONFIG.FEATURES,
  });
}
