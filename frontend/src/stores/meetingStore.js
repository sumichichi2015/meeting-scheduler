import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { format } from 'date-fns'
import { ja } from 'date-fns/locale'

export const useMeetingStore = defineStore('meeting', () => {
  const currentMeeting = ref(null)
  const participants = ref([])
  const loading = ref(false)
  const error = ref(null)

  const datetimeSlots = computed(() => {
    if (!currentMeeting.value) return []
    
    const slots = []
    const startTime = parseInt(currentMeeting.value.startTime.split(':')[0])
    const endTime = parseInt(currentMeeting.value.endTime.split(':')[0])
    
    currentMeeting.value.dates.forEach(date => {
      for (let hour = startTime; hour < endTime; hour++) {
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

  async function createMeeting(meetingData) {
    try {
      loading.value = true
      const response = await fetch('http://localhost:3002/meetings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: meetingData.name,
          organizer: meetingData.organizer,
          dates: meetingData.dates,
          start_time: meetingData.startTime,
          end_time: meetingData.endTime
        })
      })

      if (!response.ok) {
        throw new Error('会議の作成に失敗しました')
      }

      const data = await response.json()
      currentMeeting.value = {
        id: data.id,
        name: data.name,
        organizer: data.organizer,
        dates: data.dates,
        startTime: data.start_time,
        endTime: data.end_time,
        participants: []
      }

      return currentMeeting.value
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function getMeeting(id) {
    try {
      loading.value = true
      const response = await fetch(`http://localhost:3002/meetings/${id}`)
      if (!response.ok) {
        throw new Error('会議が見つかりません')
      }

      const data = await response.json()
      currentMeeting.value = {
        id: data.id,
        name: data.name,
        organizer: data.organizer,
        dates: data.dates,
        startTime: data.start_time,
        endTime: data.end_time,
        participants: data.participants || []
      }
      participants.value = data.participants || []

      return currentMeeting.value
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function addParticipant(participantData) {
    try {
      loading.value = true
      const response = await fetch(`http://localhost:3002/meetings/${currentMeeting.value.id}/participants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: participantData.name,
          comment: participantData.comment,
          availability: participantData.availability
        })
      })

      if (!response.ok) {
        throw new Error('参加者の追加に失敗しました')
      }

      const data = await response.json()
      participants.value.push({
        name: data.name,
        comment: data.comment,
        availability: data.availability
      })

      return data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    currentMeeting,
    participants,
    loading,
    error,
    datetimeSlots,
    createMeeting,
    getMeeting,
    addParticipant
  }
})
