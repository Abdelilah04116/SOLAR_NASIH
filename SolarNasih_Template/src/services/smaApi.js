// src/services/smaApi.js
// Fonction pour envoyer un message au backend SMA
export async function sendChatMessage(message) {
  // Ajoute un log pour vérifier l'appel côté frontend
  console.log('Envoi au SMA:', message);
  // Vérifie l'URL et le format du body
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, context: {} }),
  });
  if (!response.ok) {
    throw new Error('Erreur SMA : ' + response.statusText);
  }
  return response.json();
}
