import shortid from "shortid";
import { ChatMessageType } from "../store/store";
export type MessageType = "text" | "image_url" | "document"; // Ajoutez "document" ici

export function createMessage(role: "user" | "assistant", content: string, type: MessageType) {
  return {
    role,
    content,
    type,
    id: `${Date.now()}-${Math.random()}`,
  };
}