import { IonIcon } from "@ionic/react";
import classNames from "classnames";
import { sendOutline, send, cloudUploadOutline, documentOutline, micOutline, mic, closeOutline, checkmarkOutline } from "ionicons/icons";
import { useRef, useState, useEffect } from "react";
import useChat, { useMicrophoneAlert } from "../../store/store";
import { createMessage } from "../../utils/createMessage";
import axios from "axios";
import { sendChatMessage } from "../../services/smaApi"; // Ajoute l'import correct

export default function UserQuery() {
  const [query, setQuery] = useState("");
  const [importedFiles, setImportedFiles] = useState<File[]>([]); // State for multiple files
  const formRef = useRef<null | HTMLFormElement>(null);
  const addChat = useChat((state) => state.addChat);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0); // secondes
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioBlobRef = useRef<Blob | null>(null);
  
  // États pour les alertes personnalisées
  const [showRecordingStarted, setShowRecordingStarted] = useState(false);
  const [showRecordingStopped, setShowRecordingStopped] = useState(false);
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // État global pour l'alerte microphone
  const { showMicrophoneAlert, setShowMicrophoneAlert } = useMicrophoneAlert();

  // Écouter l'événement de démarrage d'enregistrement
  useEffect(() => {
    const handleStartRecording = () => {
      console.log('🎤 Événement de démarrage d\'enregistrement reçu');
      startRecording();
    };

    window.addEventListener('startMicrophoneRecording', handleStartRecording);
    return () => {
      window.removeEventListener('startMicrophoneRecording', handleStartRecording);
    };
  }, []);

  useEffect(() => {
    if (isRecording) {
      setRecordingTime(0);
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [isRecording]);

  function handleOnKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    const target = e.target as HTMLTextAreaElement;
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (formRef.current) {
        formRef.current.requestSubmit();
        target.style.height = "30px";
      }
    }
  }

  function handleOnInputChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    const target = e.target as HTMLTextAreaElement;
    setQuery(target.value);
    target.style.height = "0px";
    target.style.height = `${target.scrollHeight}px`;
  }

  async function handleOnSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    
    // Si un enregistrement est en cours, l'arrêter d'abord
    if (isRecording) {
      stopRecordingAndSend();
      // Attendre un peu que l'audio soit prêt
      setTimeout(() => {
        if (audioBlobRef.current) {
          sendAudioToBackend(audioBlobRef.current);
          audioBlobRef.current = null;
          setRecordingTime(0);
          audioChunksRef.current = [];
        }
      }, 100);
      return;
    }
    
    // Si un audio est prêt, l'envoyer
    if (audioBlobRef.current) {
      sendAudioToBackend(audioBlobRef.current);
      audioBlobRef.current = null;
      setRecordingTime(0);
      audioChunksRef.current = [];
      if (textareaRef.current) textareaRef.current.style.height = "30px";
      return;
    }
    
    // Traitement combiné : fichiers + texte
    if (importedFiles.length > 0 || query) {
      // Construire le message utilisateur combiné
      let userMessage = "";
      if (query) {
        userMessage += query;
      }
      if (importedFiles.length > 0) {
        if (userMessage) userMessage += "\n\n";
        userMessage += `Documents joints : ${importedFiles.map(f => f.name).join(", ")}`;
      }
      
      // Ajouter le message utilisateur
      addChat(createMessage("user", userMessage, "text"));
      
      try {
        // Upload des fichiers d'abord si présents
        if (importedFiles.length > 0) {
          addChat(createMessage("assistant", "📄 Indexation des documents par l'agent spécialisé...", "text"));
          
          for (const file of importedFiles) {
            try {
              console.log('🚀 Upload document:', file.name);
              const formData = new FormData();
              formData.append('file', file);
              
              const response = await fetch('http://localhost:8000/upload-document', {
                method: 'POST',
                body: formData,
              });
              
              if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Erreur upload:', response.status, errorText);
                addChat(createMessage("assistant", `❌ Erreur lors de l'indexation de "${file.name}": ${response.status}`, "text"));
              } else {
                const result = await response.json();
                console.log('✅ Document indexé:', result);
                addChat(createMessage("assistant", `✅ Document "${file.name}" indexé avec succès par l'agent spécialisé.`, "text"));
              }
            } catch (error) {
              console.error('❌ Erreur upload document:', error);
              const errorMessage = error instanceof Error ? error.message : String(error);
              addChat(createMessage("assistant", `❌ Erreur lors de l'indexation de "${file.name}": ${errorMessage}`, "text"));
            }
          }
        }
        
        // Envoyer le message avec contexte des documents
        const messageToSend = query || "Analysez les documents joints";
        const res = await sendChatMessage(messageToSend);
        addChat(createMessage("assistant", res.answer || res.message || "Aucune réponse reçue.", "text"));
        
      } catch (err: any) {
        addChat(createMessage("assistant", "Erreur SMA : " + (err.message || "Erreur inconnue"), "text"));
      }
      
      // Nettoyer l'interface
      setQuery("");
      setImportedFiles([]);
      if (textareaRef.current) textareaRef.current.style.height = "30px";
    }
  }

  function handleImportClick() {
    document.getElementById("import-file")?.click();
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (files) {
      setImportedFiles((prevFiles) => [...prevFiles, ...Array.from(files)]); // Add multiple files
    }
  }

  function handleVoiceClick() {
    if (!isRecording) {
      // Afficher l'alerte personnalisée pour demander la permission
      setShowMicrophoneAlert(true);
    } else {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop();
        setIsRecording(false);
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
      }
    }
  }

  function startRecording() {
    console.log('🎤 Démarrage de l\'enregistrement...');
    // Ne plus fermer l'alerte ici car elle est gérée globalement
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then((stream) => {
        console.log('✅ Permission microphone accordée');
        streamRef.current = stream;
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];
        
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };
        
        mediaRecorder.onstop = () => {
          console.log('🛑 Enregistrement arrêté');
          // Essayer d'enregistrer en WAV, sinon utiliser WebM
          const mimeType = MediaRecorder.isTypeSupported('audio/wav') ? 'audio/wav' : 'audio/webm';
          const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
          audioBlobRef.current = audioBlob;
          setShowRecordingStopped(true);
          setTimeout(() => setShowRecordingStopped(false), 3000);
        };
        
        mediaRecorder.start();
        setIsRecording(true);
        setShowRecordingStarted(true);
        setTimeout(() => setShowRecordingStarted(false), 3000);
      })
      .catch((err) => {
        console.error('❌ Erreur microphone:', err);
        setErrorMessage("Impossible d'accéder au micro : " + err.message);
        setShowError(true);
        setTimeout(() => setShowError(false), 5000);
      });
  }

  function stopRecordingAndSend() {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    }
  }

  async function sendAudioToBackend(audioBlob: Blob) {
    try {
      // Afficher un message de traitement
      addChat(createMessage("assistant", "🎤 Traitement de votre message vocal par l'agent spécialisé...", "text"));
      
      // Créer un FormData pour envoyer l'audio
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.webm');
      
      // Envoyer au backend SMA pour traitement par l'agent audio
      const response = await fetch('http://localhost:8000/voice-chat', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Réponse agent audio:', result);
        console.log('🔍 Clés disponibles:', Object.keys(result));
        
        // Extraire le texte transcrit de la réponse (gérer plusieurs clés possibles)
        const transcribedText = result.transcription || result.transcribed_text || result.text || result.message || "Texte non reconnu";
        console.log('📝 Texte transcrit extrait:', transcribedText);
        
        // Placer le texte transcrit dans le champ de saisie
        setQuery(transcribedText);
        
        // Ajuster la hauteur du textarea
        if (textareaRef.current) {
          textareaRef.current.style.height = "0px";
          textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
        
        // Mettre le focus sur le textarea
        if (textareaRef.current) {
          textareaRef.current.focus();
        }
        
        // Confirmation de succès
        addChat(createMessage("assistant", "✅ Message vocal converti en texte et placé dans le champ de saisie.", "text"));
        
      } else {
        const errorText = await response.text();
        console.error('❌ Erreur agent audio:', response.status, errorText);
        throw new Error(`Erreur agent audio: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('❌ Erreur lors du traitement audio:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      addChat(createMessage("assistant", `❌ Erreur lors de la conversion audio : ${errorMessage}`, "text"));
    }
  }

  return (
    <div>
      {showRecordingStarted && (
        <div className="fixed top-4 right-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-6 py-4 rounded-xl shadow-2xl z-50 animate-slideInRight border border-green-400">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-white rounded-full mr-3 animate-pulse shadow-lg"></div>
            <div>
              <span className="font-semibold text-sm">🎤 Enregistrement en cours</span>
              <p className="text-xs opacity-90">Parlez maintenant, SolarNasih vous écoute...</p>
            </div>
          </div>
        </div>
      )}

      {showRecordingStopped && (
        <div className="fixed top-4 right-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-4 rounded-xl shadow-2xl z-50 animate-slideInRight border border-blue-400">
          <div className="flex items-center">
            <IonIcon icon={checkmarkOutline} className="mr-3 text-xl" />
            <div>
              <span className="font-semibold text-sm">✅ Enregistrement terminé</span>
              <p className="text-xs opacity-90">Traitement par l'agent vocal en cours...</p>
            </div>
          </div>
        </div>
      )}

      {showError && (
        <div className="fixed top-4 right-4 bg-gradient-to-r from-red-500 to-pink-600 text-white px-6 py-4 rounded-xl shadow-2xl z-50 animate-slideInRight border border-red-400 max-w-sm">
          <div className="flex items-start">
            <IonIcon icon={closeOutline} className="mr-3 text-xl mt-0.5 flex-shrink-0" />
            <div>
              <span className="font-semibold text-sm">❌ Erreur microphone</span>
              <p className="text-xs opacity-90 mt-1">{errorMessage}</p>
            </div>
          </div>
        </div>
      )}

      {/* Display imported files above the chat */}
      <div className="mb-4">
        {importedFiles.map((file, index) => (
          <div key={index} className="flex items-center mb-2">
            <IonIcon icon={documentOutline} className="text-gray-600 dark:text-white" />
            <span className="ml-2 text-sm text-gray-600 dark:text-white">{file.name}</span>
          </div>
        ))}
      </div>
      <form
        className="input shadow-md dark:bg-[#40414f] bg-white dark:border-white border-gray-700 border-2 flex items-center rounded-md"
        onSubmit={handleOnSubmit}
        ref={formRef}
      >
        <div className="w-1/12 text-center mx-2">
          <button
            type="button"
            className="text-center text-gray-600 dark:text-white transition inline-flex items-center justify-center py-2 px-2 rounded-md"
            onClick={handleImportClick}
          >
            <IonIcon icon={cloudUploadOutline} />
          </button>
          <input
            type="file"
            id="import-file"
            accept=".json"
            multiple // Allow multiple file selection
            className="hidden"
            onChange={handleFileChange}
          />
        </div>
        <div className="w-8/12 p-2">
          <textarea
            name="query"
            ref={textareaRef}
            className="h-6 px-2 w-full outline-none resize-none dark:bg-transparent dark:text-white placeholder:font-bold"
            placeholder="Send a message"
            onKeyDown={handleOnKeyDown}
            onChange={handleOnInputChange}
            value={query}
            autoFocus
          ></textarea>
        </div>
        <div className="w-1/12 text-center mx-2 flex flex-col items-center justify-center">
          <button
            type="button"
            className={classNames(
              "text-center transition inline-flex items-center justify-center py-2 px-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700",
              { 
                "recording-pulse text-red-600 dark:text-red-400": isRecording,
                "text-gray-600 dark:text-white": !isRecording
              }
            )}
            onClick={handleVoiceClick}
          >
            <IonIcon icon={isRecording ? mic : micOutline} />
          </button>
          {isRecording && (
            <span className="text-xs text-red-600 dark:text-red-400 font-bold mt-1 animate-pulse">
              {Math.floor(recordingTime / 60).toString().padStart(2, '0')}:{(recordingTime % 60).toString().padStart(2, '0')}
            </span>
          )}
        </div>
        <div className="w-1/12 text-center mx-2">
          <button
            type="submit"
            className={classNames(
              "text-center text-gray-600 dark:text-white transition inline-flex items-center justify-center py-2 px-2 rounded-md",
              { "bg-green-500 dark:text-gray-200 text-white": query || importedFiles.length > 0 }
            )}
          >
            <IonIcon icon={query || importedFiles.length > 0 ? send : sendOutline} />
          </button>
        </div>
      </form>
    </div>
  );
}