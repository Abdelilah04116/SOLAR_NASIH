export async function sendChatMessage(message) {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: message })
  });
  if (!response.ok) {
    throw new Error('Erreur réseau : ' + response.status);
  }
  return await response.json();
}
