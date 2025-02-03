import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://meeting-scheduler-backend.fly.dev';

export const useMeetingStore = defineStore('meeting', () => {
  const currentMeeting = ref(null);
  const error = ref(null);
  const loading = ref(false);

  async function createMeeting(meetingData) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await axios.post(`${API_BASE_URL}/meetings`, {
        name: meetingData.name,
        organizer: meetingData.organizer,
        dates: meetingData.dates,
        start_time: meetingData.startTime,
        end_time: meetingData.endTime,
        created_at: new Date().toISOString()
      });

      if (!response.data || !response.data.id) {
        throw new Error('サーバーからの応答が不正です');
      }

      currentMeeting.value = response.data;
      console.log('Meeting created:', response.data);
      return response.data;
    } catch (e) {
      console.error('API Error:', e);
      error.value = e.response?.data?.detail || 'エラーが発生しました';
      throw error.value;
    } finally {
      loading.value = false;
    }
  }

  async function getMeeting(id, retryCount = 3) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await axios.get(`${API_BASE_URL}/meetings/${id});
      
      if (!response.data) {
        throw new Error('会議データが見つかりません');
      }

      currentMeeting.value = response.data;
      return response.data;
    } catch (e) {
      console.error('API Error:', e);
      if (retryCount > 0) {
        console.log(`Retrying... (${retryCount} attempts left)`);
        await new Promise(resolve => setTimeout(resolve, 1000));
        return getMeeting(id, retryCount - 1);
      }
      error.value = e.response?.data?.detail || '会議情報の取得に失敗しました';
      throw error.value;
    } finally {
      loading.value = false;
    }
  }

  async function addParticipant(meetingId, participantData) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/meetings/${meetingId}/participants`,
        participantData
      );
      
      if (!response.data) {
        throw new Error('参加者の登録に失敗しました');
      }

      currentMeeting.value = response.data;
      return response.data;
    } catch (e) {
      console.error('API Error:', e);
      error.value = e.response?.data?.detail || '参加登録に失敗しました';
      throw error.value;
    } finally {
      loading.value = false;
    }
  }

  return {
    currentMeeting,
    error,
    loading,
    createMeeting,
    getMeeting,
    addParticipant
  };
});
