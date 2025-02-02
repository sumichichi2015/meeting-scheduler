<template>
  <div class="join-meeting">
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <div v-if="meetingStore.loading" class="loading">
      読み込み中...
    </div>

    <template v-else>
      <div class="meeting-header">
        <h2>{{ meetingStore.currentMeeting?.name }}</h2>
        <p class="organizer">主催者: {{ meetingStore.currentMeeting?.organizer }}</p>
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
          <label for="comment">コメント (30文字以内)</label>
          <input
            id="comment"
            v-model="comment"
            type="text"
            maxlength="30"
            placeholder="例：遅れて参加する可能性あり"
          >
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
                <th v-for="participant in meetingStore.participants" :key="participant.name">
                  {{ participant.name }}
                </th>
                <th v-if="!hasSubmitted">あなたの予定</th>
              </tr>
              <tr class="comment-row">
                <th class="time-header">コメント</th>
                <td v-for="participant in meetingStore.participants" :key="participant.name" class="comment-cell">
                  {{ participant.comment }}
                </td>
                <td v-if="!hasSubmitted" class="comment-cell">
                  {{ comment }}
                </td>
              </tr>
            </thead>
            <tbody>
              <tr v-for="datetime in meetingStore.datetimeSlots" :key="datetime.key">
                <td class="time-cell">{{ formatDateTime(datetime) }}</td>
                <td v-for="participant in meetingStore.participants" :key="participant.name"
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

      <div class="participants-list" v-if="meetingStore.participants.length > 0">
        <h3>参加者コメント</h3>
        <div v-for="participant in meetingStore.participants" :key="participant.name" class="participant">
          <div class="participant-name">{{ participant.name }}</div>
          <div class="participant-comment">{{ participant.comment }}</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMeetingStore } from '../stores/meetingStore'
import { format } from 'date-fns'
import { ja } from 'date-fns/locale'

const route = useRoute()
const meetingStore = useMeetingStore()
const participantName = ref('')
const comment = ref('')
const hasSubmitted = ref(false)
const availability = ref({})
const errorMessage = ref('')

// ドラッグ選択関連の状態
const isDragging = ref(false)
const dragStart = ref(null)
const selectedCells = ref(new Set())

onMounted(async () => {
  try {
    await meetingStore.getMeeting(route.params.id)
  } catch (error) {
    errorMessage.value = '会議情報の取得に失敗しました'
    console.error('Error fetching meeting:', error)
  }
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

function startDrag(event) {
  if (!event.target.classList.contains('editable')) return
  isDragging.value = true
  dragStart.value = {
    date: event.target.dataset.date,
    time: event.target.dataset.time
  }
  
  const key = `${dragStart.value.date}-${dragStart.value.time}`
  const currentValue = availability.value[key] || '○'
  availability.value[key] = getNextAvailability(currentValue)
  selectedCells.value = new Set([key])
}

function handleDrag(event) {
  if (!isDragging.value) return
  const cell = event.target
  if (!cell.classList.contains('editable')) return

  const date = cell.dataset.date
  const time = cell.dataset.time
  if (!date || !time) return

  const key = `${date}-${time}`
  if (selectedCells.value.has(key)) return

  const startKey = Array.from(selectedCells.value)[0]
  const [startDate, startTime] = startKey.split('-')
  const targetValue = availability.value[`${startDate}-${startTime}`]
  availability.value[key] = targetValue
  selectedCells.value.add(key)
}

function endDrag() {
  isDragging.value = false
  selectedCells.value.clear()
}

function isSelected(date, time) {
  return selectedCells.value.has(`${date}-${time}`)
}

function setSelectedAvailability(value) {
  selectedCells.value.forEach(key => {
    const [date, time] = key.split('-')
    if (!availability.value[date]) {
      availability.value[date] = {}
    }
    availability.value[date][time] = value
  })
  selectedCells.value.clear()
}

function getNextAvailability(current) {
  const order = ['○', '△', '×']
  const currentIndex = order.indexOf(current)
  return order[(currentIndex + 1) % order.length]
}

const isValid = computed(() => participantName.value.trim().length > 0)

async function submitSchedule() {
  if (!isValid.value) return

  try {
    await meetingStore.addParticipant({
      name: participantName.value,
      comment: comment.value,
      availability: availability.value
    })
    hasSubmitted.value = true
  } catch (error) {
    errorMessage.value = '参加登録に失敗しました'
    console.error('Error submitting schedule:', error)
  }
}
</script>

<style scoped>
.join-meeting {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.error-message {
  background-color: #fde8e8;
  color: #c53030;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.meeting-header {
  margin-bottom: 30px;
  text-align: center;
}

.meeting-header h2 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.organizer {
  color: #666;
}

.participant-form {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #4a5568;
}

input[type="text"],
textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 16px;
}

.schedule-section {
  margin: 20px 0;
}

.schedule-table {
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: center;
  border: 1px solid #e2e8f0;
}

.time-header {
  background-color: #f7fafc;
  font-weight: bold;
  position: sticky;
  left: 0;
  z-index: 2;
}

.time-cell {
  background-color: #f7fafc;
  position: sticky;
  left: 0;
  z-index: 1;
  white-space: nowrap;
}

.schedule-cell {
  cursor: pointer;
  transition: background-color 0.2s;
}

.schedule-cell.editable {
  cursor: pointer;
}

.schedule-cell.available {
  background-color: #c6f6d5;
}

.schedule-cell.maybe {
  background-color: #fefcbf;
}

.schedule-cell.unavailable {
  background-color: #fed7d7;
}

.comment-row {
  background-color: #f7fafc;
}

.comment-cell {
  font-size: 14px;
  color: #666;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.controls {
  display: flex;
  gap: 20px;
  align-items: center;
  justify-content: flex-end;
  margin-top: 20px;
  padding: 0 20px;
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
  background-color: #c6f6d5;
}

.control-button.maybe {
  background-color: #fefcbf;
}

.control-button.unavailable {
  background-color: #fed7d7;
}

.submit-button {
  padding: 8px 20px;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-button:hover {
  background-color: #3182ce;
}

.submit-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.participants-list {
  margin-top: 30px;
}

.participant {
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 10px;
}

.participant-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.participant-comment {
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .join-meeting {
    padding: 10px;
  }

  .schedule-table {
    margin: 20px -10px;
  }

  th,
  td {
    padding: 8px;
    font-size: 14px;
  }

  .controls {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
