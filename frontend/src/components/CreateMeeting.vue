<template>
  <div class="create-meeting">
    <h2>新しい会議を作成</h2>
    <form @submit.prevent="createMeeting" v-if="!isLoading">
      <div class="form-group">
        <label for="name">会議名</label>
        <input
          type="text"
          id="name"
          v-model="formData.name"
          required
          maxlength="100"
          placeholder="例：プロジェクトキックオフ"
        >
      </div>

      <div class="form-group">
        <label for="organizer">主催者名</label>
        <input
          type="text"
          id="organizer"
          v-model="formData.organizer"
          required
          maxlength="50"
          placeholder="例：山田太郎"
        >
      </div>

      <div class="form-group">
        <label>候補日</label>
        <div class="date-picker">
          <input
            type="date"
            v-model="selectedDate"
            :min="minDate"
            @change="addDate"
          >
        </div>
        <div class="selected-dates" v-if="formData.dates.length > 0">
          <div v-for="(date, index) in formData.dates" :key="date" class="date-tag">
            {{ formatDate(date) }}
            <button type="button" @click="removeDate(index)" class="remove-date">&times;</button>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label>時間帯</label>
        <div class="time-range">
          <select v-model="formData.startTime">
            <option v-for="time in timeOptions" :key="time" :value="time">
              {{ time }}
            </option>
          </select>
          <span>〜</span>
          <select v-model="formData.endTime">
            <option v-for="time in timeOptions" :key="time" :value="time">
              {{ time }}
            </option>
          </select>
        </div>
      </div>

      <div class="error-message" v-if="error">{{ error }}</div>

      <button type="submit" :disabled="!isValid">会議を作成</button>
    </form>

    <div v-else class="loading">
      会議を作成中...
    </div>

    <div v-if="createdMeetingUrl" class="success-message">
      <p>会議を作成しました！</p>
      <div class="share-url">
        <input type="text" readonly :value="createdMeetingUrl">
        <button @click="copyUrl">URLをコピー</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useMeetingStore } from '../stores/meetingStore';
import { useRouter } from 'vue-router';

export default {
  name: 'CreateMeeting',
  
  setup() {
    const meetingStore = useMeetingStore();
    const router = useRouter();
    const error = ref('');
    const selectedDate = ref('');
    const createdMeetingUrl = ref('');
    const isLoading = ref(false);

    const formData = ref({
      name: '',
      organizer: '',
      dates: [],
      startTime: '09:00',
      endTime: '10:00'
    });

    // 時間オプションの生成（30分間隔）
    const timeOptions = computed(() => {
      const times = [];
      for (let hour = 0; hour < 24; hour++) {
        for (let minute of ['00', '30']) {
          times.push(`${String(hour).padStart(2, '0')}:${minute}`);
        }
      }
      return times;
    });

    // 最小日付（今日）
    const minDate = computed(() => {
      const today = new Date();
      return today.toISOString().split('T')[0];
    });

    // フォームバリデーション
    const isValid = computed(() => {
      return formData.value.name &&
             formData.value.organizer &&
             formData.value.dates.length > 0 &&
             formData.value.startTime &&
             formData.value.endTime;
    });

    // 日付のフォーマット
    const formatDate = (dateStr) => {
      const date = new Date(dateStr);
      return date.toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    };

    // 日付の追加
    const addDate = () => {
      if (selectedDate.value && !formData.value.dates.includes(selectedDate.value)) {
        formData.value.dates.push(selectedDate.value);
        formData.value.dates.sort();
        selectedDate.value = '';
      }
    };

    // 日付の削除
    const removeDate = (index) => {
      formData.value.dates.splice(index, 1);
    };

    // URLのコピー
    const copyUrl = async () => {
      try {
        await navigator.clipboard.writeText(createdMeetingUrl.value);
        alert('URLをコピーしました！');
      } catch (err) {
        console.error('URLのコピーに失敗しました:', err);
      }
    };

    // 会議の作成
    const createMeeting = async () => {
      try {
        isLoading.value = true;
        error.value = '';
        
        const response = await meetingStore.createMeeting(formData.value);
        console.log('Created meeting response:', response);
        
        if (response && response.id) {
          const baseUrl = window.location.origin;
          createdMeetingUrl.value = `${baseUrl}/meetings/${response.id}`;
          router.push(`/meetings/${response.id}`);
        } else {
          throw new Error('会議の作成に失敗しました');
        }
      } catch (err) {
        console.error('Error creating meeting:', err);
        error.value = err.message || '会議の作成に失敗しました。もう一度お試しください。';
      } finally {
        isLoading.value = false;
      }
    };

    return {
      formData,
      selectedDate,
      timeOptions,
      minDate,
      error,
      isLoading,
      createdMeetingUrl,
      isValid,
      formatDate,
      addDate,
      removeDate,
      copyUrl,
      createMeeting
    };
  }
};
</script>

<style scoped>
.create-meeting {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input[type="text"],
input[type="date"],
select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.time-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.time-range select {
  width: 100px;
}

.selected-dates {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.date-tag {
  background-color: #e9ecef;
  padding: 5px 10px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.remove-date {
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  padding: 0 5px;
}

.error-message {
  color: #dc3545;
  margin-bottom: 10px;
}

.success-message {
  margin-top: 20px;
  padding: 15px;
  background-color: #d4edda;
  border-radius: 4px;
}

.share-url {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.share-url input {
  flex: 1;
}

button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #6c757d;
}
</style>
