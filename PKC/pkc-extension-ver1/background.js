console.log('PKC Background script is running');

let currentActivity = null;

chrome.runtime.onInstalled.addListener(() => {
  console.log('PKC Extension installed');
  chrome.storage.local.set({ activities: [], summaries: {}, connections: [] });
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Message received:', request);
  
  switch(request.action) {
    case "startActivity":
      startActivity(request.activity);
      sendResponse({status: 'success'});
      break;
    case "summarize":
      summarizePage(request.content, request.url, sender.tab.id);
      sendResponse({status: 'success'});
      break;
    case "addMemo":
      addMemo(request.memo, request.url);
      sendResponse({status: 'success'});
      break;
    case "endActivity":
      endActivity();
      sendResponse({status: 'success'});
      break;
  }
  
  return true;  // Indicates that the response will be sent asynchronously
});

async function startActivity(activity) {
  currentActivity = activity;
  await chrome.storage.local.set({ currentActivity: activity, summaries: {} });
  console.log(`Activity started: ${activity}`);
}

async function summarizePage(content, url, tabId) {
  console.log(`Summarizing page: ${url}`);
  
  // Simple summarization (replace with AI-based summarization in production)
  const summary = content.split('.').slice(0, 3).join('.') + '.';

  const { summaries } = await chrome.storage.local.get('summaries');
  summaries[url] = { summary, memos: [] };
  await chrome.storage.local.set({ summaries });

  // Send the summary to the content script
  chrome.tabs.sendMessage(tabId, { action: "updateSummary", summary });

  console.log(`Page summarized: ${url}`);
}

async function addMemo(memo, url) {
  const { summaries } = await chrome.storage.local.get('summaries');
  if (summaries[url]) {
    summaries[url].memos.push(memo);
    await chrome.storage.local.set({ summaries });
    console.log(`Memo added to ${url}`);
  } else {
    console.log(`No summary found for ${url}. Creating new entry.`);
    summaries[url] = { summary: '', memos: [memo] };
    await chrome.storage.local.set({ summaries });
  }
}

async function endActivity() {
  try {
    const { summaries } = await chrome.storage.local.get('summaries');
    const documents = Object.entries(summaries).map(([url, data]) => ({
      url,
      summary: data.summary,
      memos: data.memos
    }));

    // Simple connection generation (replace with AI-based in production)
    const connections = ["Connection 1", "Connection 2"];
    const overallSummary = "This is an overall summary of your activity.";

    await chrome.storage.local.set({
      currentActivity: null,
      finalReport: {
        activity: currentActivity,
        summaries,
        connections,
        overallSummary
      }
    });

    currentActivity = null;

    console.log('Activity ended, final report generated');
    // You can add logic here to display the final report
  } catch (error) {
    console.error('Error ending activity:', error);
  }
}