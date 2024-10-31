document.addEventListener('DOMContentLoaded', () => {
  const activitySelect = document.getElementById('activity-select');
  const startButton = document.getElementById('start-button');
  const memoInput = document.getElementById('memo-input');
  const addMemoButton = document.getElementById('add-memo-button');
  const endActivityButton = document.getElementById('end-activity-button');
  const summaryContent = document.getElementById('summary-content');

  function sendMessage(message) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(message, response => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else {
          resolve(response);
        }
      });
    });
  }

  chrome.storage.local.get('currentActivity', (data) => {
    if (data.currentActivity) {
      activitySelect.value = data.currentActivity;
      activitySelect.disabled = true;
      startButton.disabled = true;
      endActivityButton.disabled = false;
    } else {
      endActivityButton.disabled = true;
    }
  });

  startButton.addEventListener('click', async () => {
    const activity = activitySelect.value;
    if (activity) {
      try {
        await sendMessage({ action: "startActivity", activity });
        activitySelect.disabled = true;
        startButton.disabled = true;
        endActivityButton.disabled = false;
      } catch (error) {
        console.error('Error starting activity:', error);
      }
    }
  });

  addMemoButton.addEventListener('click', async () => {
    const memo = memoInput.value;
    if (memo) {
      try {
        await sendMessage({ 
          action: "addMemo", 
          memo, 
          url: window.location.href 
        });
        memoInput.value = '';
      } catch (error) {
        console.error('Error adding memo:', error);
      }
    }
  });

  endActivityButton.addEventListener('click', async () => {
    try {
      await sendMessage({ action: "endActivity" });
      activitySelect.disabled = false;
      startButton.disabled = false;
      endActivityButton.disabled = true;
      activitySelect.value = '';
    } catch (error) {
      console.error('Error ending activity:', error);
    }
  });

  // Listen for summary updates
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "updateSummary") {
      summaryContent.textContent = request.summary;
    }
  });
});