import { useCallback, useEffect, useRef, useState } from "react";
import { ChatMessageType } from "../store/store";

interface UseBotProps {
  index: number;
  chat: ChatMessageType;
}

interface UseBotReturn {
  result: string;
  error: string | null;
  isStreamCompleted: boolean;
  cursorRef: React.RefObject<HTMLSpanElement>;
}

export default function useBot({ index, chat }: UseBotProps): UseBotReturn {
  const [result, setResult] = useState<string>(chat.content || "");
  const [error, setError] = useState<string | null>(null);
  const [isStreamCompleted, setIsStreamCompleted] = useState<boolean>(false);
  const cursorRef = useRef<HTMLSpanElement>(null);

  const processBotResponse = useCallback(async () => {
    if (chat.content || result) return;

    try {
      setError(null);
      setIsStreamCompleted(false);
      
      // Simuler une réponse du bot (à remplacer par votre API réelle)
      const mockResponse = "Je suis Solar Nasih, votre assistant en énergie solaire. Comment puis-je vous aider aujourd'hui ?";
      
      // Simulation du streaming
      let currentText = "";
      const words = mockResponse.split(" ");
      
      for (let i = 0; i < words.length; i++) {
        currentText += (i > 0 ? " " : "") + words[i];
        setResult(currentText);
        await new Promise(resolve => setTimeout(resolve, 100)); // Délai entre les mots
      }
      
      setIsStreamCompleted(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Une erreur est survenue");
      setIsStreamCompleted(true);
    }
  }, [chat.content, result]);

  useEffect(() => {
    processBotResponse();
  }, [processBotResponse]);

  return {
    result,
    error,
    isStreamCompleted,
    cursorRef,
  };
} 