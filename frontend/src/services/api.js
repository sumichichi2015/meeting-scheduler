import axios from 'axios';

const API_BASE_URL = 'http://localhost:3002';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const meetingApi = {
  // 会議を作成
  createMeeting: async (meetingData) => {
    try {
      const response = await api.post('/meetings', meetingData);
      return response.data;
    } catch (error) {
      console.error('会議作成エラー:', error);
      throw error;
    }
  },

  // 会議の詳細を取得
  getMeeting: async (meetingId) => {
    try {
      const response = await api.get(`/meetings/${meetingId}`);
      return response.data;
    } catch (error) {
      console.error('会議取得エラー:', error);
      throw error;
    }
  },

  // 参加者を追加
  addParticipant: async (meetingId, participantData) => {
    try {
      const response = await api.post(
        `/meetings/${meetingId}/participants`,
        participantData
      );
      return response.data;
    } catch (error) {
      console.error('参加者追加エラー:', error);
      throw error;
    }
  },

  // 参加者一覧を取得
  getParticipants: async (meetingId) => {
    try {
      const response = await api.get(`/meetings/${meetingId}/participants`);
      return response.data;
    } catch (error) {
      console.error('参加者一覧取得エラー:', error);
      throw error;
    }
  }
};
