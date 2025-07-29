import { IonIcon } from "@ionic/react";
import { sendOutline } from "ionicons/icons";
import useChat from "../../store/store";
import classNames from "classnames";
import { createMessage } from "../../utils/createMessage";
import { sendChatMessage } from "../../services/smaApi";
import { useState } from "react";

export default function DefaultIdea({
  ideas,
  myclassNames,
}: {
  ideas: { idea: string; moreContext: string }[];
  myclassNames?: string;
}) {
  const addChat = useChat((state) => state.addChat);
  const [loadingIdeas, setLoadingIdeas] = useState<Set<string>>(new Set());
  
  const handleIdeaClick = async (idea: { idea: string; moreContext: string }) => {
    // Éviter les clics multiples
    if (loadingIdeas.has(idea.idea)) return;
    
    // Marquer cette idée comme en cours de chargement
    setLoadingIdeas(prev => new Set(prev).add(idea.idea));
    
    // Ajouter le message utilisateur
    addChat(createMessage("user", idea.moreContext, "text"));
    
    // Ajouter un message d'assistant vide pour montrer le chargement
    addChat(createMessage("assistant", "", "text"));
    
    try {
      // Envoyer la requête au backend SMA
      const res = await sendChatMessage(idea.moreContext);
      
      // Remplacer le message vide par la vraie réponse
      addChat(createMessage("assistant", res.answer || res.message || "Aucune réponse reçue.", "text"));
      
    } catch (err: any) {
      // En cas d'erreur, remplacer par un message d'erreur
      addChat(createMessage("assistant", "Erreur SMA : " + (err.message || "Erreur inconnue"), "text"));
    } finally {
      // Retirer de l'état de chargement
      setLoadingIdeas(prev => {
        const newSet = new Set(prev);
        newSet.delete(idea.idea);
        return newSet;
      });
    }
  };
  
  return (
    <div
      className={classNames(
        "md:grid md:grid-cols-2 md:grid-rows-1 md:items-stretch md:gap-2 ",
        myclassNames
      )}
    >
      {ideas.map((i) => {
        const isLoading = loadingIdeas.has(i.idea);
        return (
          <button
            key={i.idea}
            disabled={isLoading}
            className={classNames(
              "border inline-flex dark:border-gray-500 border-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 mb-2 w-full text-left p-2 group rounded-md shadow flex-1 md:flex-row md:items-center transition-all duration-200",
              {
                "opacity-50 cursor-not-allowed": isLoading,
                "hover:bg-blue-50 dark:hover:bg-blue-900/20": !isLoading
              }
            )}
            onClick={() => handleIdeaClick(i)}
          >
            <div className="self-stretch w-11/12">
              <h3 className="font-bold dark:text-gray-300 text-gray-700">
                {i.idea}
              </h3>
              <p className="dark:text-gray-400 text-gray-600">{i.moreContext}</p>
            </div>

            <div className="btn text-gray-600 dark:text-gray-200 text-lg invisible duration-75 transition-all group-hover:visible">
              {isLoading ? (
                <div className="animate-spin w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
              ) : (
                <IonIcon icon={sendOutline} />
              )}
            </div>
          </button>
        );
      })}
    </div>
  );
}
