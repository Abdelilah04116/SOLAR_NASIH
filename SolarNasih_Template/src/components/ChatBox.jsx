import React, { useState } from 'react';
import { sendChatMessage } from '../services/smaApi';

const ChatComponent = () => {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSend = async () => {
    setLoading(true);
    setError('');
    setResponse('');
    try {
      // Ajoute un log pour vérifier l'appel côté React
      console.log('handleSend appelé avec:', input);
      if (!sendChatMessage || typeof sendChatMessage !== 'function') {
        setError('Erreur SMA : sendChatMessage n\'est pas correctement importé ou défini.');
        setLoading(false);
        return;
      }
      const res = await sendChatMessage(input);
      setResponse(res.answer || res.message || 'Aucune réponse');
    } catch (err) {
      if (err.message && err.message.includes('Failed to fetch')) {
        setError('Erreur SMA : Impossible de contacter le backend SMA. Vérifiez que le serveur SMA est bien démarré sur http://localhost:8000 et que CORS est activé.');
      } else {
        setError('Erreur SMA : ' + (err.message || err.toString()));
      }
    }
    setLoading(false);
  };

  return (
    <div>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Tapez votre message ici..."
      />
      <button onClick={handleSend} disabled={loading || !input.trim()}>
        {loading ? 'Envoi...' : 'Envoyer'}
      </button>
      <div>
        <strong>Réponse SMA:</strong> {response}
      </div>
      {error && <div style={{color: 'red'}}>{error}</div>}
    </div>
  );
};

export default ChatComponent;