console.log('PKC Content script is running');

let sidebarInjected = false;

function injectSidebar() {
  if (sidebarInjected) return;
  
  console.log('Injecting sidebar');
  
  const sidebar = document.createElement('div');
  sidebar.id = 'pkc-sidebar';
  sidebar.innerHTML = 'Loading PKC Companion...';
  
  const toggle = document.createElement('button');
  toggle.id = 'pkc-toggle';
  toggle.textContent = '>>';
  
  document.body.appendChild(sidebar);
  document.body.appendChild(toggle);

  console.log('Sidebar and toggle button appended to body');

  fetch(chrome.runtime.getURL('sidebar.html'))
    .then(response => response.text())
    .then(data => {
      console.log('Sidebar HTML fetched:', data.substring(0, 100) + '...'); // Log first 100 chars
      sidebar.innerHTML = data;
      sidebarInjected = true;
      console.log('Sidebar HTML injected');
      initializeSidebar();
    })
    .catch(error => console.error('Error fetching sidebar HTML:', error));

  toggle.addEventListener('click', () => {
    console.log('Toggle button clicked');
    sidebar.classList.toggle('open');
    toggle.textContent = sidebar.classList.contains('open') ? '<<' : '>>';
    console.log('Sidebar open state:', sidebar.classList.contains('open'));
  });
}

function initializeSidebar() {
  console.log('Initializing sidebar');
  const activitySelect = document.getElementById('activity-select');
  const startButton = document.getElementById('start-button');
  const memoInput = document.getElementById('memo-input');
  const addMemoButton = document.getElementById('add-memo-button');
  const endActivityButton = document.getElementById('end-activity-button');
  const summaryContent = document.getElementById('summary-content');

  if (!activitySelect || !startButton || !memoInput || !addMemoButton || !endActivityButton || !summaryContent) {
    console.error('Some sidebar elements are missing');
    console.log('activitySelect:', activitySelect);
    console.log('startButton:', startButton);
    console.log('memoInput:', memoInput);
    console.log('addMemoButton:', addMemoButton);
    console.log('endActivityButton:', endActivityButton);
    console.log('summaryContent:', summaryContent);
    return;
  }

  startButton.addEventListener('click', startActivity);
  addMemoButton.addEventListener('click', addMemo);
  endActivityButton.addEventListener('click', endActivity);

  chrome.storage.local.get('currentActivity', (data) => {
    console.log('Current activity data:', data);
    if (data.currentActivity) {
      activitySelect.value = data.currentActivity;
      activitySelect.disabled = true;
      startButton.disabled = true;
      endActivityButton.disabled = false;
    } else {
      endActivityButton.disabled = true;
    }
  });

  // Request page summary
  chrome.runtime.sendMessage({
    action: "summarize",
    content: document.body.innerText,
    url: window.location.href
  });

  console.log('Sidebar initialized');
}

function startActivity() {
  console.log('Starting activity');
  const activity = document.getElementById('activity-select').value;
  if (activity) {
    chrome.runtime.sendMessage({ action: "startActivity", activity }, (response) => {
      console.log('Start activity response:', response);
      if (response && response.status === 'success') {
        document.getElementById('activity-select').disabled = true;
        document.getElementById('start-button').disabled = true;
        document.getElementById('end-activity-button').disabled = false;
      }
    });
  }
}

function addMemo() {
  console.log('Adding memo');
  const memo = document.getElementById('memo-input').value;
  if (memo) {
    chrome.runtime.sendMessage({
      action: "addMemo",
      memo,
      url: window.location.href
    }, (response) => {
      console.log('Add memo response:', response);
      if (response && response.status === 'success') {
        document.getElementById('memo-input').value = '';
      }
    });
  }
}

function endActivity() {
  console.log('Ending activity');
  chrome.runtime.sendMessage({ action: "endActivity" }, (response) => {
    console.log('End activity response:', response);
    if (response && response.status === 'success') {
      document.getElementById('activity-select').disabled = false;
      document.getElementById('start-button').disabled = false;
      document.getElementById('end-activity-button').disabled = true;
      document.getElementById('activity-select').value = '';
    }
  });
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Message received in content script:', request);
  if (request.action === "updateSummary") {
    const summaryContent = document.getElementById('summary-content');
    if (summaryContent) {
      summaryContent.textContent = request.summary;
      console.log('Summary updated');
    } else {
      console.error('Summary content element not found');
    }
  }
});

// Inject sidebar when the content script loads
injectSidebar();

// Add this line to check if the script is running after navigation
console.log('Content script finished running');