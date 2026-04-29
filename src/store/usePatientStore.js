import { create } from 'zustand';
import apiClient from '../api/client';

const usePatientStore = create((set, get) => ({
  patientId: null,
  profile: null,
  chatHistory: [],
  isLoading: false,
  verificationOtp: '123 456', // Dummy for now, should be fetched/generated

  // Action pour activer l'app via ID/QR
  setPatientId: async (id) => {
    set({ isLoading: true });
    try {
      const response = await apiClient.get(`/patient/${id}/profile`);
      set({ 
        patientId: id, 
        profile: response.data,
        isLoading: false 
      });
      return true;
    } catch (error) {
      set({ isLoading: false });
      return false;
    }
  },

  // Action pour envoyer un message à l'IA
  sendMessage: async (text) => {
    const { patientId } = get();
    try {
      const response = await apiClient.post('/ai/chat', {
        patient_id: patientId,
        patient_symptoms: text,
        include_glossary: true
      });
      return response.data;
    } catch (error) {
      console.error('Chat error:', error);
      throw error;
    }
  },

  logout: () => set({ patientId: null, profile: null, chatHistory: [] })
}));

export default usePatientStore;
