<template>
  <div class="join-meeting">
    <div class="meeting-header">
      <h2>{{ meeting.name }}</h2>
      <p class="organizer">主催者: {{ meeting.organizer }}</p>
    </div>

    <div class="schedule-container">
      <div class="fixed-header">
        <div class="form-group">
          <label for="participantName">お名前 (10文字以内)</label>
          <input
            id="participantName"
            v-model="participantName"
            type="text"
            required
            placeholder="例：山田太郎"
          >
        </div>
        <div class="form-group">
          <label for="comment">コメント (100文字以内)</label>
          <textarea
            id="comment"
            v-model="comment"
            maxlength="100"
            rows="4"
            style="width: 100%; min-height: 100px; resize: vertical;"
            placeholder="例：遅れて参加する可能性あり"
          ></textarea>
        </div>
      </div>

      <div class="schedule-table-container">
        <table class="schedule-table">
          <thead>
            <tr class="fixed-row">
              <th class="date-cell">日時</th>
              <th v-for="participant in participants" :key="participant.name">
                {{ participant.name }}
              </th>
              <th v-if="!hasSubmitted">あなたの予定</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(datetime, index) in datetimeSlots" :key="index"
                :class="{ 'new-date': index > 0 && datetimeSlots[index-1].date !== datetime.date }">
              <td class="date-time-cell">
                {{ formatDateTime(datetime) }}
              </td>
              <td v-for="participant in participants" :key="participant.name">
                {{ getParticipantAvailability(participant, datetime) }}
              </td>
              <td v-if="!hasSubmitted" 
                  class="availability-cell"
                  :class="getCellClass('current', datetime)"
                  @mousedown="startDrag($event, 'current', datetime)"
                  @mouseover="handleDrag($event, 'current', datetime)"
                  @mouseup="endDrag"
                  @mouseleave="endDrag">
                {{ getAvailabilitySymbol(datetime.date, datetime.time) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="controls" v-if="!hasSubmitted">
      <div class="availability-controls">
        <button @click="setSelectedAvailability('○')" class="control-button available">○</button>
        <button @click="setSelectedAvailability('△')" class="control-button maybe">△</button>
        <button @click="setSelectedAvailability('×')" class="control-button unavailable">×</button>
      </div>
      <button @click="submitSchedule" :disabled="!isValid" class="submit-button">
        予定を送信
      </button>
    </div>

    <div class="participants-list" v-if="participants.length > 0">
      <h3>参加者コメント</h3>
      <div v-for="participant in participants" :key="participant.name" class="participant">
        <div class="participant-name">{{ participant.name }}</div>
        <div class="participant-comment">{{ participant.comment }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { format } from 'date-fns'
import { ja } from 'date-fns/locale'

// 仮のデータ
const meeting = ref({
  name: '週次ミーティング',
  organizer: '山田太郎',
  dates: ['2025-02-01', '2025-02-02', '2025-02-03']
})

const participants = ref([
  {
    name: '田中一郎',
    comment: '午前中であれば参加可能',
    availability: {
      '2025-02-01-09:00': '○',
      '2025-02-01-09:30': '○',
      '2025-02-01-10:00': '△',
      '2025-02-01-10:30': '×'
    }
  }
])

// ドラッグ関連の状態管理
const dragState = ref({
  isDragging: false,
  startCell: null,
  participantId: null,
  selectedCells: new Set()
});

const startDrag = (event, participantId, datetime) => {
  dragState.value = {
    isDragging: true,
    startCell: datetime,
    participantId: participantId,
    selectedCells: new Set([datetime])
  };
};

const handleDrag = (event, participantId, datetime) => {
  if (!dragState.value.isDragging || dragState.value.participantId !== participantId) return;
  dragState.value.selectedCells.add(datetime);
};

const endDrag = () => {
  if (!dragState.value.isDragging) return;

  const availability = dragState.value.participantId === 'current' 
    ? availability.value 
    : participants.value.find(p => p.id === dragState.value.participantId)?.availability;

  if (!availability) return;

  // 選択されたセルの現在の状態を取得
  const currentStates = Array.from(dragState.value.selectedCells).map(datetime => 
    availability[datetime] || 'unavailable'
  );

  // 全てのセルが同じ状態かチェック
  const allSameState = currentStates.every(state => state === currentStates[0]);
  
  // 次の状態を決定
  let nextState;
  if (allSameState) {
    // 全て同じ状態なら、次の状態に進める
    const states = ['unavailable', 'available', 'maybe'];
    const currentIndex = states.indexOf(currentStates[0]);
    nextState = states[(currentIndex + 1) % states.length];
  } else {
    // 異なる状態が混在している場合は、最初の状態（○）にする
    nextState = 'available';
  }

  // 選択された全てのセルを更新
  dragState.value.selectedCells.forEach(datetime => {
    availability[datetime] = nextState;
  });

  // ドラッグ状態をリセット
  dragState.value = {
    isDragging: false,
    startCell: null,
    participantId: null,
    selectedCells: new Set()
  };
};

// セルのクラスを取得
const getCellClass = (participantId, datetime) => {
  const isSelected = dragState.value.isDragging && 
                    dragState.value.participantId === participantId && 
                    dragState.value.selectedCells.has(datetime);
  
  const availability = participantId === 'current' 
    ? availability.value[datetime] 
    : participants.value.find(p => p.id === participantId)?.availability[datetime];

  return {
    'available': availability === '○',
    'maybe': availability === '△',
    'unavailable': !availability || availability === '×',
    'selected': isSelected
  };
};

// 日時スロットの生成
const datetimeSlots = computed(() => {
  const slots = []
  meeting.value.dates.forEach(date => {
    for (let hour = 9; hour < 18; hour++) {
      for (let minute of [0, 30]) {
        const time = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
        slots.push({
          date,
          time,
          key: `${date}-${time}`
        })
      }
    }
  })
  return slots
})

const participantName = ref('')
const comment = ref('')
const hasSubmitted = ref(false)
const availability = ref({})

const isValid = computed(() => {
  return participantName.value.length > 0
})

function formatDateTime(datetime) {
  const date = new Date(datetime.date)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const dayOfWeek = ['日', '月', '火', '水', '木', '金', '土'][date.getDay()]
  return `${month}/${day}(${dayOfWeek}) ${datetime.time}`
}

function getParticipantAvailability(participant, datetime) {
  const key = `${datetime.date}-${datetime.time}`
  return participant.availability?.[key] || '○'
}

function getAvailabilitySymbol(date, time) {
  const key = `${date}-${time}`
  return availability.value[date]?.[time] || '○'
}

function setSelectedAvailability(value) {
  // 選択されたセルの現在の状態を取得
  const currentStates = Array.from(dragState.value.selectedCells).map(datetime => 
    availability.value[datetime] || 'unavailable'
  );

  // 全てのセルが同じ状態かチェック
  const allSameState = currentStates.every(state => state === currentStates[0]);
  
  // 次の状態を決定
  let nextState;
  if (allSameState) {
    // 全て同じ状態なら、次の状態に進める
    const states = ['unavailable', 'available', 'maybe'];
    const currentIndex = states.indexOf(currentStates[0]);
    nextState = states[(currentIndex + 1) % states.length];
  } else {
    // 異なる状態が混在している場合は、最初の状態（○）にする
    nextState = 'available';
  }

  // 選択された全てのセルを更新
  dragState.value.selectedCells.forEach(datetime => {
    availability.value[datetime] = nextState;
  });

  // ドラッグ状態をリセット
  dragState.value = {
    isDragging: false,
    startCell: null,
    participantId: null,
    selectedCells: new Set()
  };
}

async function submitSchedule() {
  participants.value.push({
    name: participantName.value,
    comment: comment.value,
    availability: { ...availability.value }
  })
  
  hasSubmitted.value = true
  participantName.value = ''
  comment.value = ''
}
</script>

<style scoped>
.join-meeting {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.meeting-header {
  margin-bottom: 20px;
}

.schedule-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 20px;
}

.fixed-header {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.schedule-table-container {
  position: relative;
  overflow: auto;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.schedule-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.schedule-table thead {
  position: sticky;
  top: 0;
  z-index: 2;
  background: white;
}

.schedule-table th {
  padding: 10px;
  text-align: center;
  background: white;
  border-bottom: 2px solid #ddd;
  white-space: nowrap;
}

.schedule-table td {
  padding: 6px;
  text-align: center;
  border: 1px solid #ddd;
  white-space: nowrap;
}

.date-time-cell {
  text-align: left;
  padding: 6px 10px;
  white-space: nowrap;
  position: sticky;
  left: 0;
  background: white;
  z-index: 1;
  min-width: 120px;
  border-right: 2px solid #ddd;
}

.availability-cell {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 1px solid #ddd;
  transition: background-color 0.2s;
}

.availability-cell.selected {
  background-color: rgba(0, 123, 255, 0.1);
  border: 2px solid #007bff;
}

.availability-cell.available {
  background-color: #e8f5e9;
}

.availability-cell.maybe {
  background-color: #fff3e0;
}

.availability-cell.unavailable {
  background-color: #ffebee;
}

/* 参加者コメントのスタイル */
.participant-comment {
  font-size: 0.8em;
  color: #666;
  white-space: normal;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* コントロールボタンのスタイル */
.control-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.2rem;
}

.control-button.available {
  background-color: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
}

.control-button.maybe {
  background-color: rgba(255, 193, 7, 0.1);
  color: #FFC107;
}

.control-button.unavailable {
  background-color: rgba(244, 67, 54, 0.1);
  color: #f44336;
}

.submit-button {
  padding: 8px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.participants-list {
  margin-top: 30px;
}

.participant {
  padding: 15px;
  border-bottom: 1px solid #ddd;
}

.participant-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.participant-comment {
  color: #666;
}

.comment-row {
  font-size: 0.85rem;
  color: #666;
  background-color: #f9f9f9;
}

.comment-cell {
  padding: 4px 8px;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.comment-cell:hover {
  white-space: normal;
  word-wrap: break-word;
  position: relative;
}

.comment-cell:hover::after {
  content: attr(title);
  position: absolute;
  left: 0;
  top: 100%;
  background: white;
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 10;
  max-width: 200px;
  white-space: normal;
}

.date-divider {
  border-top: 2px solid #666;
  margin-top: 10px;
  padding-top: 15px;
}

.time-slot {
  width: 60px;
}

@media (max-width: 768px) {
  .schedule-table {
    font-size: 0.9rem;
  }

  th, td {
    padding: 8px;
    min-width: 80px;
  }

  .controls {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
