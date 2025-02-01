<template>
  <div class="join-meeting">
    <div class="meeting-header">
      <h2>{{ meeting.name }}</h2>
      <p class="organizer">主催者: {{ meeting.organizer }}</p>
    </div>

    <div class="participant-form" v-if="!hasSubmitted">
      <div class="form-group">
        <label for="participantName">お名前 (10文字以内)</label>
        <input
          id="participantName"
          v-model="participantName"
          type="text"
          maxlength="10"
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
          rows="3"
          placeholder="例：遅れて参加する可能性あり"
        ></textarea>
      </div>
    </div>

    <div class="schedule-section">
      <div class="schedule-table"
           @mousedown="startDrag"
           @mousemove="handleDrag"
           @mouseup="endDrag"
           @mouseleave="endDrag">
        <table>
          <thead>
            <tr>
              <th class="time-header">日時</th>
              <th v-for="participant in participants" :key="participant.name">
                {{ participant.name }}
              </th>
              <th v-if="!hasSubmitted">あなたの予定</th>
            </tr>
            <tr class="comment-row">
              <th class="time-header">コメント</th>
              <td v-for="participant in participants" :key="participant.name" class="comment-cell">
                {{ participant.comment }}
              </td>
              <td v-if="!hasSubmitted" class="comment-cell">
                {{ comment }}
              </td>
            </tr>
          </thead>
          <tbody>
            <tr v-for="datetime in datetimeSlots" :key="datetime.key">
              <td class="time-cell">{{ formatDateTime(datetime) }}</td>
              <td v-for="participant in participants" :key="participant.name"
                  class="schedule-cell">
                {{ getParticipantAvailability(datetime.date, datetime.time, participant) }}
              </td>
              <td v-if="!hasSubmitted"
                  class="schedule-cell editable"
                  :class="[
                    getAvailabilityClass(datetime.date, datetime.time),
                    { 'cell-selected': isSelected(datetime.date, datetime.time) }
                  ]"
                  :data-date="datetime.date"
                  :data-time="datetime.time">
                {{ getAvailabilitySymbol(datetime.date, datetime.time) }}
              </td>
            </tr>
          </tbody>
        </table>
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

// ドラッグ選択関連の状態
const isDragging = ref(false)
const dragStart = ref(null)
const selectedCells = ref(new Set())

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
  return `${format(date, 'M/d(E)', { locale: ja })} ${datetime.time}`
}

function getParticipantAvailability(date, time, participant) {
  const key = `${date}-${time}`
  return participant.availability?.[key] || '○'
}

function getAvailabilitySymbol(date, time) {
  const key = `${date}-${time}`
  return availability.value[key] || '○'
}

function getAvailabilityClass(date, time) {
  const key = `${date}-${time}`
  const value = availability.value[key]
  return {
    'available': !value || value === '○',
    'maybe': value === '△',
    'unavailable': value === '×'
  }
}

// ドラッグ選択関連の関数
function startDrag(event) {
  if (!event.target.classList.contains('editable')) return
  isDragging.value = true
  dragStart.value = {
    date: event.target.dataset.date,
    time: event.target.dataset.time
  }
  
  // ドラッグ開始点の状態を変更
  const key = `${dragStart.value.date}-${dragStart.value.time}`
  const currentValue = availability.value[key] || '○'
  availability.value[key] = getNextAvailability(currentValue)
  selectedCells.value = new Set([key])
}

function handleDrag(event) {
  if (!isDragging.value) return
  const cell = event.target
  if (!cell.classList.contains('editable')) return

  const currentDate = cell.dataset.date
  const currentTime = cell.dataset.time
  if (!currentDate || !currentTime) return

  const key = `${currentDate}-${currentTime}`
  if (selectedCells.value.has(key)) return

  // 新しいセルの状態を、ドラッグ開始点と同じ状態に変更
  selectedCells.value.add(key)
  const startKey = `${dragStart.value.date}-${dragStart.value.time}`
  const targetValue = availability.value[startKey]
  availability.value[key] = getNextAvailability(targetValue)
}

function endDrag() {
  isDragging.value = false
}

function isSelected(date, time) {
  return selectedCells.value.has(`${date}-${time}`)
}

function setSelectedAvailability(value) {
  selectedCells.value.forEach(key => {
    availability.value[key] = value
  })
  selectedCells.value.clear()
}

function getNextAvailability(current) {
  const order = ['○', '△', '×']
  const currentIndex = order.indexOf(current)
  return order[(currentIndex + 1) % order.length]
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

.participant-form {
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.schedule-section {
  margin-bottom: 30px;
}

.schedule-table {
  overflow-x: auto;
  margin-bottom: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: center;
  min-width: 100px;
}

.time-header {
  background: #f5f5f5;
  position: sticky;
  left: 0;
  z-index: 2;
}

.time-cell {
  background: #f5f5f5;
  position: sticky;
  left: 0;
  z-index: 1;
  white-space: nowrap;
}

.schedule-cell {
  position: relative;
  cursor: default;
}

.schedule-cell.editable {
  cursor: pointer;
  user-select: none;
}

.cell-selected {
  position: relative;
}

.cell-selected::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
  pointer-events: none;
}

.controls {
  display: flex;
  gap: 20px;
  align-items: center;
  justify-content: flex-end;
  margin-top: 20px;
}

.availability-controls {
  display: flex;
  gap: 10px;
}

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
