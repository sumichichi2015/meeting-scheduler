<template>
  <div class="create-meeting">
    <h2>会議作成</h2>
    <div class="form-container">
      <div class="form-group">
        <label for="meetingName">会議名 (20文字以内)</label>
        <input
          id="meetingName"
          v-model="meetingName"
          type="text"
          maxlength="20"
          required
          placeholder="例：週次ミーティング"
        >
      </div>

      <div class="form-group">
        <label for="organizerName">主催者名 (10文字以内)</label>
        <input
          id="organizerName"
          v-model="organizerName"
          type="text"
          maxlength="10"
          required
          placeholder="例：山田太郎"
        >
      </div>

      <div class="date-time-section">
        <h3>候補日時の選択</h3>
        
        <div class="calendar-container">
          <v-calendar
            v-model="selectedDates"
            :min-date="new Date()"
            :max-date="maxDate"
            :attributes="calendarAttributes"
            :columns="2"
            mode="multiple"
            is-expanded
            :first-day-of-week="1"
            :locale="ja"
            @dayclick="onDayClick"
          />
        </div>

        <div class="time-slots-container">
          <h4>時間帯の設定</h4>
          <div class="time-slots-header">
            <div class="time-range">
              <label>
                開始時刻:
                <select v-model="defaultStartTime">
                  <option v-for="time in availableStartTimes" :key="time" :value="time">
                    {{ time }}
                  </option>
                </select>
              </label>
              <label>
                終了時刻:
                <select v-model="defaultEndTime">
                  <option v-for="time in availableEndTimes" :key="time" :value="time">
                    {{ time }}
                  </option>
                </select>
              </label>
            </div>
            <div class="time-controls">
              <button @click="applyTimeToAllDates" class="apply-time-button">
                全ての日に適用
              </button>
              <button @click="clearAllTimeSlots" class="clear-button">
                全ての時間帯をクリア
              </button>
            </div>
          </div>

          <div class="selected-dates-list">
            <div v-for="date in selectedDates" :key="date" class="date-item">
              <div class="date-header">
                {{ formatDate(date) }}
                <button @click="removeDate(date)" class="remove-date-button">×</button>
              </div>
              <div class="time-slots"
                   @mousedown="e => startDragOnTimeSlots(e, date)"
                   @mousemove="e => handleDragOnTimeSlots(e, date)"
                   @mouseup="endDragOnTimeSlots"
                   @mouseleave="endDragOnTimeSlots">
                <div v-for="time in timeSlots" :key="time" 
                     class="time-slot"
                     :class="{ 
                       selected: isTimeSelected(date, time), 
                       'drag-selected': isDragSelected(date, time)
                     }"
                     :data-time="time">
                  <span>{{ time }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button
          @click="createMeeting"
          :disabled="!isValid"
          class="create-button"
        >
          会議を作成
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { format, addMonths } from 'date-fns'
import { ja } from 'date-fns/locale'

const meetingName = ref('')
const organizerName = ref('')
const selectedDates = ref([])
const selectedTimeSlots = ref({}) // { '2025-02-01': ['09:00', '09:30', ...] }
const defaultStartTime = ref('09:00')
const defaultEndTime = ref('18:00')
const startDate = ref('')
const endDate = ref('')

const maxDate = computed(() => addMonths(new Date(), 2))
const today = computed(() => format(new Date(), 'yyyy-MM-dd'))

const timeSlots = computed(() => {
  const slots = []
  for (let hour = 9; hour < 18; hour++) {
    slots.push(`${String(hour).padStart(2, '0')}:00`)
    slots.push(`${String(hour).padStart(2, '0')}:30`)
  }
  return slots
})

const availableStartTimes = computed(() => {
  return timeSlots.value.slice(0, -1)
})

const availableEndTimes = computed(() => {
  return timeSlots.value.slice(1)
})

const calendarAttributes = computed(() => [{
  dot: true,
  dates: selectedDates.value.map(date => new Date(date)),
  class: 'selected-date'
}])

const isValid = computed(() => {
  return (
    meetingName.value.trim().length > 0 &&
    organizerName.value.trim().length > 0 &&
    selectedDates.value.length > 0 &&
    Object.values(selectedTimeSlots.value).some(times => times.length > 0)
  )
})

function formatDate(date) {
  return format(new Date(date), 'M月d日(E)', { locale: ja })
}

function isTimeSelected(date, time) {
  return selectedTimeSlots.value[date]?.includes(time) || false
}

function toggleTimeSlot(date, time) {
  if (!selectedTimeSlots.value[date]) {
    selectedTimeSlots.value[date] = []
  }

  const index = selectedTimeSlots.value[date].indexOf(time)
  const updatedSlots = { ...selectedTimeSlots.value }
  
  if (index === -1) {
    updatedSlots[date] = [...updatedSlots[date], time]
  } else {
    updatedSlots[date] = updatedSlots[date].filter(t => t !== time)
  }
  
  selectedTimeSlots.value = updatedSlots
}

function removeDate(date) {
  const index = selectedDates.value.indexOf(date)
  if (index !== -1) {
    selectedDates.value.splice(index, 1)
    delete selectedTimeSlots.value[date]
  }
}

function applyTimeToAllDates() {
  const startIndex = timeSlots.value.indexOf(defaultStartTime.value)
  const endIndex = timeSlots.value.indexOf(defaultEndTime.value)
  
  if (startIndex === -1 || endIndex === -1 || startIndex >= endIndex) return

  const selectedTimes = timeSlots.value.slice(startIndex, endIndex + 1)
  
  selectedDates.value.forEach(date => {
    selectedTimeSlots.value[date] = [...selectedTimes]
  })
}

function generateDateRange() {
  if (!startDate.value || !endDate.value) return
  
  const start = new Date(startDate.value)
  const end = new Date(endDate.value)
  const dates = []
  
  let current = start
  while (current <= end && dates.length < 15) {
    dates.push(format(current, 'yyyy-MM-dd'))
    current.setDate(current.getDate() + 1)
  }
  
  selectedDates.value = dates
  dates.forEach(date => {
    if (!selectedTimeSlots.value[date]) {
      selectedTimeSlots.value[date] = []
    }
  })
}

function clearAllTimeSlots() {
  selectedTimeSlots.value = {}
  selectedDates.value.forEach(date => {
    selectedTimeSlots.value[date] = []
  })
}

function clearDateTimeSlots(date) {
  selectedTimeSlots.value[date] = []
}

const isDragging = ref(false)
const dragStartTime = ref(null)
const dragCurrentTime = ref(null)
const dragCurrentDate = ref(null)
const draggedCells = ref(new Set())

function startDragOnTimeSlots(event, date) {
  const timeSlot = event.target.closest('.time-slot')
  if (!timeSlot) return
  
  const time = timeSlot.dataset.time
  if (!time || !selectedTimeSlots.value[date]?.includes(time)) return

  event.preventDefault()
  isDragging.value = true
  dragStartTime.value = time
  dragCurrentTime.value = time
  dragCurrentDate.value = date
  updateDraggedCells()
}

function handleDragOnTimeSlots(event, date) {
  if (!isDragging.value || date !== dragCurrentDate.value) return

  const timeSlot = event.target.closest('.time-slot')
  if (!timeSlot) return

  const time = timeSlot.dataset.time
  if (!time) return

  dragCurrentTime.value = time
  updateDraggedCells()
}

function updateDraggedCells() {
  const times = timeSlots.value
  const startIdx = times.indexOf(dragStartTime.value)
  const currentIdx = times.indexOf(dragCurrentTime.value)
  
  const [fromIdx, toIdx] = startIdx <= currentIdx 
    ? [startIdx, currentIdx] 
    : [currentIdx, startIdx]

  const newDraggedCells = new Set()
  for (let i = fromIdx; i <= toIdx; i++) {
    const time = times[i]
    if (selectedTimeSlots.value[dragCurrentDate.value]?.includes(time)) {
      newDraggedCells.add(`${dragCurrentDate.value}-${time}`)
    }
  }
  draggedCells.value = newDraggedCells
}

function endDragOnTimeSlots() {
  if (!isDragging.value) return

  if (draggedCells.value.size > 0) {
    const newTimeSlots = {}
    Object.entries(selectedTimeSlots.value).forEach(([date, times]) => {
      if (date === dragCurrentDate.value) {
        newTimeSlots[date] = times.filter(time => 
          !draggedCells.value.has(`${date}-${time}`))
      } else {
        newTimeSlots[date] = [...times]
      }
    })
    selectedTimeSlots.value = newTimeSlots
  }

  isDragging.value = false
  dragStartTime.value = null
  dragCurrentTime.value = null
  dragCurrentDate.value = null
  draggedCells.value.clear()
}

function isDragSelected(date, time) {
  return draggedCells.value.has(`${date}-${time}`)
}

function onDayClick(day) {
  const date = format(day.date, 'yyyy-MM-dd')
  const index = selectedDates.value.indexOf(date)
  
  if (index === -1) {
    selectedDates.value.push(date)
    selectedTimeSlots.value[date] = []
  } else {
    selectedDates.value.splice(index, 1)
    delete selectedTimeSlots.value[date]
  }
}

async function createMeeting() {
  const meetingData = {
    name: meetingName.value,
    organizer: organizerName.value,
    dates: selectedDates.value,
    timeSlots: selectedTimeSlots.value
  }

  console.log('Meeting created:', meetingData)
  // TODO: API実装後に追加
}
</script>

<style scoped>
.create-meeting {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.form-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.date-time-section {
  margin-top: 30px;
}

.calendar-container {
  margin-bottom: 2rem;
}

:deep(.selected-date) {
  background-color: rgba(76, 175, 80, 0.1);
  border: 2px solid #4CAF50;
  border-radius: 4px;
}

:deep(.vc-day) {
  cursor: pointer;
}

:deep(.vc-day:hover) {
  background-color: rgba(0, 0, 0, 0.05);
}

.time-slots-container {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
}

.time-slots-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.time-range {
  display: flex;
  gap: 20px;
}

.time-range select {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.apply-time-button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.apply-time-button:hover {
  background-color: #45a049;
}

.selected-dates-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.date-item {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.remove-date-button {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 1.2rem;
}

.remove-date-button:hover {
  color: #f44336;
}

.time-slots {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 8px;
  padding: 8px;
  user-select: none;
}

.time-slot {
  position: relative;
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  user-select: none;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  text-align: center;
}

.time-slot.selected {
  background-color: rgba(76, 175, 80, 0.1);
  border-color: #4CAF50;
}

.time-slot.drag-selected {
  background-color: rgba(244, 67, 54, 0.1);
  border-color: #f44336;
  transform: scale(0.95);
}

.time-slot:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.time-slot label {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
}

.time-slot input[type="checkbox"] {
  margin: 0;
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.create-button {
  padding: 12px 24px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1.1rem;
}

.create-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.date-range-inputs {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: flex-end;
}

.date-input {
  flex: 1;
}

.date-input label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.date-input input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.generate-dates-button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  height: 37px;
}

.time-controls {
  display: flex;
  gap: 10px;
}

.clear-button {
  padding: 8px 16px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.clear-date-button {
  padding: 4px 8px;
  background-color: #ff9800;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.date-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

@media (max-width: 768px) {
  .time-slots-header {
    flex-direction: column;
    gap: 10px;
  }

  .time-range {
    flex-direction: column;
    gap: 10px;
  }

  .selected-dates-list {
    grid-template-columns: 1fr;
  }
}
</style>
