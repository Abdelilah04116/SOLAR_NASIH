import { ChatMessageType, ModalList, useSettings } from "../store/store";

const apiUrl = "http://0.0.0.0:8000";
const IMAGE_GENERATION_API_URL = "http://0.0.0.0:8000";

export async function fetchResults(
  messages: Omit<ChatMessageType, "id" | "type">[],
  modal: string,
  signal: AbortSignal,
  onData: (data: any) => void,
  onCompletion: () => void
) {
  try {
    const response = await fetch(apiUrl, {
      method: `POST`,
      signal: signal,
      headers: {
        "content-type": `application/json`,
        accept: `text/event-stream`,
        Authorization: `Bearer ${localStorage.getItem("apikey")}`,
      },
      body: JSON.stringify({
        model: useSettings.getState().settings.selectedModal,
        temperature: 0.7,
        stream: true,
        messages: messages,
      }),
    });

    if (response.status !== 200) {
      console.log(response);
      throw new Error("Error fetching results");
    }
    const reader: any = response.body?.getReader();
    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        onCompletion();
        break;
      }

      let chunk = new TextDecoder("utf-8").decode(value, { stream: true });

      const chunks = chunk.split("\n").filter((x: string) => x !== "");

      chunks.forEach((chunk: string) => {
        if (chunk === "data: [DONE]") {
          return;
        }
        if (!chunk.startsWith("data: ")) return;
        chunk = chunk.replace("data: ", "");
        const data = JSON.parse(chunk);
        if (data.choices[0].finish_reason === "stop") return;
        onData(data.choices[0].delta.content);
      });
    }
  } catch (error) {
    if (error instanceof DOMException || error instanceof Error) {
      throw new Error(error.message);
    }
  }
}

export async function fetchModals() {
  try {
    const response = await fetch("http://0.0.0.0:8000", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("apikey")}`,
      },
    });
    const data = await response.json();
    return data;
  } catch (error) {
    if (error instanceof DOMException || error instanceof Error) {
      throw new Error(error.message);
    }
  }
}

export type ImageSize =
  | "256x256"
  | "512x512"
  | "1024x1024"
  | "1280x720"
  | "1920x1080"
  | "1024x1024"
  | "1792x1024"
  | "1024x1792";

export type IMAGE_RESPONSE = {
  created_at: string;
  data: IMAGE[];
};
export type IMAGE = {
  url: string;
};
export type DallEImageModel = Extract<ModalList, "dall-e-2" | "dall-e-3">;

export async function generateImage(
  prompt: string,
  size: ImageSize,
  numberOfImages: number
) {
  const selectedModal = useSettings.getState().settings.selectedModal;

  const response = await fetch(IMAGE_GENERATION_API_URL, {
    method: `POST`,
    // signal: signal,
    headers: {
      "content-type": `application/json`,
      accept: `text/event-stream`,
      Authorization: `Bearer ${localStorage.getItem("apikey")}`,
    },
    body: JSON.stringify({
      model: selectedModal,
      prompt: prompt,
      n: numberOfImages,
      size: useSettings.getState().settings.dalleImageSize[
        selectedModal as DallEImageModel
      ],
    }),
  });
  const body: IMAGE_RESPONSE = await response.json();
  return body;
}

// src/services/chatService.ts

// Envoie une question à l'API SMA
export async function askSMA(question: string, context: any = {}) {
  const response = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: question,
      context: context
    }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Erreur SMA");
  }
  return await response.json();
}

// Upload un document via l'API SMA
export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:8000/upload-document", {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Erreur upload document");
  }
  return await response.json();
}

// Simulation énergétique via l'API SMA
export async function simulateEnergy(simulationParams: any) {
  const response = await fetch("http://localhost:8000/simulate-energy", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(simulationParams),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Erreur simulation");
  }
  return await response.json();
}

// Liste les documents indexés via l'API SMA
export async function listDocuments() {
  const response = await fetch("http://localhost:8000/documents", {
    method: "GET",
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Erreur listing documents");
  }
  return await response.json();
}

// Supprime un document via l'API SMA
export async function deleteDocument(documentId: string) {
  const response = await fetch(`http://localhost:8000/documents/${documentId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Erreur suppression document");
  }
  return await response.json();
}
