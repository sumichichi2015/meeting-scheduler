<template>
  <div class="join-meeting">
    <div class="header" ref="header">
      <div class="participant-info">
        <div class="name-input">
          <label>お名前：</label>
          <input v-model="participantName" type="text" maxlength="20" />
        </div>
        <div class="comment-input">
          <label>コメント：</label>
          <textarea v-model="comment" maxlength="100" rows="2"></textarea>
        </div>
      </div>
      <div class="button-group">
        <button @click="submitSchedule" :disabled="!isValid">予定を送信</button>
      </div>
    </div>

    <div class="schedule-table-container" ref="tableContainer">
      <table class="schedule-table">
        <thead>
          <tr>
            <th class="name-column">参加者</th>
            <th v-for="(date, index) in meeting.value.dates" :key="date" :class="{ 'date-separator': index > 0 }">
              {{ formatDate(date) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="participant in participants.value" :key="participant.name">
            <td class="name-column">
              <div class="participant-name">{{ participant.name }}</div>
              <div class="participant-comment" v-if="participant.comment">{{ participant.comment }}</div>
            </td>
            <td v-for="(datetime, index) in datetimeSlots" 
                :key="datetime.key"
                :class="{ 'date-separator': isDateSeparator(index) }">
              <div class="availability-cell">
                {{ getParticipantAvailability(participant, datetime) }}
              </div>
            </td>
          </tr>
          <tr class="current-user">
            <td class="name-column">
              <div class="participant-name">{{ participantName || '未入力' }}</div>
              <div class="participant-comment" v-if="comment">{{ comment }}</div>
            </td>
            <td v-for="(datetime, index) in datetimeSlots" 
                :key="datetime.key"
                :class="{ 'date-separator': isDateSeparator(index) }">
              <div class="availability-cell"
                   :class="getCellClass(datetime)"
                   @mousedown="startDrag($event, datetime)"
                   @mouseover="handleDrag($event, datetime)"
                   @mouseup="endDrag"
                   @mouseleave="endDrag">
                {{ getCellValue(datetime) }}
              </div>
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
    </div>

    <div class="participants-list" v-if="participants.value.length > 0">
      <h3>参加者コメント</h3>
      <div v-for="participant in participants.value" :key="participant.name" class="participant">
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
const isDragging = ref(false)
const dragStartCell = ref(null)
const selectedCells = ref(new Set())
const dragStartValue = ref(null)

// 参加者の予定
const availability = ref({})

// ドラッグ操作の処理
const startDrag = (event, datetime) => {
  event.preventDefault()
  isDragging.value = true
  dragStartCell.value = datetime
  selectedCells.value = new Set([datetime])
  
  // ドラッグ開始時の値を保存
  dragStartValue.value = availability.value[datetime.key] || '○'
  
  // 次の状態に更新
  const nextValue = getNextValue(dragStartValue.value)
  updateCellValue(datetime, nextValue)
}

const handleDrag = (event, datetime) => {
  if (!isDragging.value) return
  
  // 既に選択済みのセルは無視
  if (selectedCells.value.has(datetime.key)) return
  
  // セルを選択状態に追加
  selectedCells.value.add(datetime.key)
  
  // ドラッグ開始時と同じ値の場合は次の値に、異なる場合は○に変更
  const currentValue = availability.value[datetime.key] || '○'
  const nextValue = currentValue === dragStartValue.value 
    ? getNextValue(currentValue)
    : '○'
  
  updateCellValue(datetime, nextValue)
}

const endDrag = () => {
  isDragging.value = false
  dragStartCell.value = null
  selectedCells.value.clear()
  dragStartValue.value = null
}

// セルの値を更新
const updateCellValue = (datetime, value) => {
  availability.value[datetime.key] = value
}

// 次の値を取得（○→△→×→○）
const getNextValue = (currentValue) => {
  const values = ['○', '△', '×']
  const currentIndex = values.indexOf(currentValue)
  return values[(currentIndex + 1) % values.length]
}

// セルのクラスを取得
const getCellClass = (datetime) => {
  const value = availability.value[datetime.key] || '○'
  return {
    'cell-selected': selectedCells.value.has(datetime.key),
    'available': value === '○',
    'maybe': value === '△',
    'unavailable': value === '×'
  }
}

// セルの値を表示
const getCellValue = (datetime) => {
  return availability.value[datetime.key] || '○'
}

const participantName = ref('')
const comment = ref('')
const hasSubmitted = ref(false)

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

function setSelectedAvailability(value) {
  // 選択されたセルの現在の状態を取得
  const currentStates = Array.from(selectedCells.value).map(datetime => 
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
  selectedCells.value.forEach(datetime => {
    availability.value[datetime] = nextState;
  });

  // ドラッグ状態をリセット
  selectedCells.value.clear()
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

function formatDate(date) {
  const dateObject = new Date(date)
  return format(dateObject, 'yyyy-MM-dd', { locale: ja })
}

function isDateSeparator(index) {
  return index > 0 && datetimeSlots.value[index - 1].date !== datetimeSlots.value[index].date
}
</script>

<style scoped>
.join-meeting {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 20px;
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

.name-column {
  position: sticky;
  left: 0;
  background: white;
  z-index: 1;
  min-width: 150px;
  padding: 8px;
  border-right: 2px solid #ddd;
}

.participant-name {
  font-weight: bold;
  margin-bottom: 4px;
}

.participant-comment {
  font-size: 0.85em;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.availability-cell {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 1px solid #ddd;
  user-select: none;
  transition: all 0.2s;
}

.availability-cell.cell-selected {
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

.date-separator {
  border-left: 2px solid #666;
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
