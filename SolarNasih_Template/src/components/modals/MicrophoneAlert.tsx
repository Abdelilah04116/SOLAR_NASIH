import { IonIcon } from "@ionic/react";
import { mic, checkmarkOutline } from "ionicons/icons";

interface MicrophoneAlertProps {
  visible: boolean;
  onCancel: () => void;
  onAuthorize: () => void;
}

export default function MicrophoneAlert({ visible, onCancel, onAuthorize }: MicrophoneAlertProps) {
  if (!visible) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center animate-fadeIn p-2 sm:p-4" 
      style={{ 
        zIndex: 99999,
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0
      }}
    >
      <div 
        className="bg-white dark:bg-gray-800 rounded-lg p-3 sm:p-4 md:p-6 w-full max-w-xs sm:max-w-sm mx-auto shadow-2xl transform transition-all animate-scaleIn" 
        style={{ 
          zIndex: 100000,
          position: 'relative'
        }}
      >
        {/* Icône microphone */}
        <div className="flex items-center justify-center mb-3 sm:mb-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-16 md:h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
            <IonIcon icon={mic} className="text-xl sm:text-2xl md:text-3xl text-blue-600 dark:text-blue-400" />
          </div>
        </div>

        {/* Titre */}
        <h3 className="text-sm sm:text-base md:text-lg font-semibold text-gray-900 dark:text-white text-center mb-2 sm:mb-3">
          Activer le microphone
        </h3>

        {/* Description */}
        <p className="text-xs sm:text-sm md:text-base text-gray-600 dark:text-gray-300 text-center mb-3 sm:mb-4 md:mb-6 leading-relaxed">
          Voulez-vous autoriser l'accès au microphone pour enregistrer un message vocal ?
        </p>

        {/* Boutons */}
        <div 
          className="flex flex-col space-y-2 sm:space-y-0 sm:flex-row sm:space-x-2 md:space-x-3" 
          style={{ 
            zIndex: 100001,
            position: 'relative'
          }}
        >
          <button
            type="button"
            onClick={onCancel}
            className="w-full sm:flex-1 px-2 sm:px-3 md:px-4 py-2 sm:py-2.5 md:py-3 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-xs sm:text-sm md:text-base font-medium border border-gray-300 dark:border-gray-600"
            style={{ 
              zIndex: 100002,
              position: 'relative'
            }}
          >
            Annuler
          </button>
          <button
            type="button"
            onClick={onAuthorize}
            className="w-full sm:flex-1 px-2 sm:px-3 md:px-4 py-2 sm:py-2.5 md:py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center justify-center text-xs sm:text-sm md:text-base font-medium border border-blue-500"
            style={{ 
              zIndex: 100002,
              position: 'relative'
            }}
          >
            <IonIcon icon={checkmarkOutline} className="mr-1 sm:mr-2 text-sm sm:text-base" />
            Autoriser
          </button>
        </div>
      </div>
    </div>
  );
} 