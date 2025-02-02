// ブラウザ通知の許可を要求
export const requestNotificationPermission = async () => {
  if (!('Notification' in window)) {
    console.warn('このブラウザは通知をサポートしていません');
    return false;
  }

  try {
    const permission = await Notification.requestPermission();
    return permission === 'granted';
  } catch (error) {
    console.error('通知の許可を取得できませんでした:', error);
    return false;
  }
};

// 通知を表示
export const showNotification = (title, options = {}) => {
  if (!('Notification' in window) || Notification.permission !== 'granted') {
    return;
  }

  try {
    new Notification(title, {
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      ...options
    });
  } catch (error) {
    console.error('通知の表示に失敗しました:', error);
  }
};

// 会議参加時の通知
export const notifyMeetingJoined = (meetingName) => {
  showNotification('会議参加完了', {
    body: `${meetingName}の日程調整に参加しました。`,
    tag: 'meeting-joined'
  });
};

// 新規参加者の通知
export const notifyNewParticipant = (meetingName, participantName) => {
  showNotification('新規参加者', {
    body: `${meetingName}に${participantName}さんが参加しました。`,
    tag: 'new-participant'
  });
};

// リマインダー通知
export const scheduleReminder = (meetingName, dueDate) => {
  const now = new Date();
  const due = new Date(dueDate);
  const timeUntilDue = due.getTime() - now.getTime();

  if (timeUntilDue <= 0) return;

  setTimeout(() => {
    showNotification('回答期限リマインダー', {
      body: `${meetingName}の回答期限が近づいています。`,
      tag: 'meeting-reminder'
    });
  }, Math.max(0, timeUntilDue - 24 * 60 * 60 * 1000)); // 24時間前に通知
};
