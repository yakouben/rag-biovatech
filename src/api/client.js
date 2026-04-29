import axios from 'axios';

// configuration du client API pour le backend Railway
const apiClient = axios.create({
  baseURL: 'https://web-production-fadce.up.railway.app/api/v1',
  headers: {
    'Content-Type': 'application/json',
    'X-Internal-Key': 'hela-secret-123', // Votre clé de sécurité
  },
  timeout: 10000,
});

export default apiClient;
