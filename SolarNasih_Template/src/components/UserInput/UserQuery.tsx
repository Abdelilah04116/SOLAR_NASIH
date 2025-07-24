import { IonIcon } from "@ionic/react";
import classNames from "classnames";
import { sendOutline, send, cloudUploadOutline, documentOutline, micOutline } from "ionicons/icons";
import { useRef, useState, useEffect } from "react";
import useChat from "../../store/store";
import { createMessage } from "../../utils/createMessage";
import axios from "axios";

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
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioBlobRef = useRef<Blob | null>(null);

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
    
    // Envoi texte SMA
    if (query) {
      addChat(createMessage("user", query, "text"));
      try {
        const res = await askSMA(query);
        addChat(createMessage("assistant", res.message || res.response || "Aucune réponse reçue.", "text"));
      } catch (err: any) {
        addChat(createMessage("assistant", "Erreur SMA : " + (err.message || "Erreur inconnue"), "text"));
      }
      setQuery("");
      if (textareaRef.current) textareaRef.current.style.height = "30px";
      return;
    }

    // Gestion de l'envoi de fichiers
    if (importedFiles.length > 0) {
      importedFiles.forEach((file) => {
        addChat(createMessage("user", file.name, "document"));
      });
      addChat(createMessage("assistant", "Processing your documents message ....", "text"));
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
      const permission = window.confirm("Voulez-vous ouvrir le micro pour enregistrer un audio ?");
      if (!permission) return;
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
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
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            audioBlobRef.current = audioBlob;
            alert("Enregistrement arrêté.");
          };
          mediaRecorder.start();
          setIsRecording(true);
          alert("Enregistrement démarré ! Parlez...");
        })
        .catch((err) => {
          alert("Impossible d'accéder au micro : " + err.message);
        });
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
      // Créer un FormData pour envoyer l'audio
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      
      // Envoyer au backend pour conversion audio vers texte
      const response = await fetch('/api/process-audio', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const result = await response.json();
        // Le backend renvoie le texte transcrit de l'audio
        const transcribedText = result.text || result.transcription || "Texte non reconnu";
        
        // Ajouter le texte transcrit comme un message utilisateur normal
        addChat(createMessage("user", transcribedText, "text"));
        
        // Ajouter une réponse d'assistant (optionnel)
        addChat(createMessage("assistant", "Traitement de votre message vocal...", "text"));
      } else {
        throw new Error('Erreur lors du traitement audio');
      }
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors de la conversion audio vers texte');
    }
  }

  return (
    <div>
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
              "text-center text-gray-600 dark:text-white transition inline-flex items-center justify-center py-2 px-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700",
              { "recording-pulse": isRecording }
            )}
            onClick={handleVoiceClick}
          >
            <IonIcon icon={micOutline} />
          </button>
          {isRecording && (
            <span className="text-xs text-red-600 font-bold mt-1">
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