import React, { useState } from 'react';
import { sendChatMessage } from '../services/smaApi';

function ChatBox() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSend = async () => {
    setLoading(true);
    setError('');
    setResponse('');
    try {
      const res = await sendChatMessage(input);
      setResponse(res.answer || res.message || 'Aucune réponse');
    } catch (err) {
      setError('Erreur lors de la communication avec le SMA : ' + (err.message || err.toString()));
    }
    setLoading(false);
  };

  return (
    <div>
      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Posez votre question..."
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
}

export default ChatBox;