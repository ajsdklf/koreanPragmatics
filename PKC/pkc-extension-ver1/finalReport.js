document.addEventListener('DOMContentLoaded', () => {
  chrome.storage.local.get('finalReport', (data) => {
    const { activity, summaries, connections, overallSummary } = data.finalReport;
    const reportContent = document.getElementById('report-content');

    reportContent.innerHTML = `
      <h2>Activity: ${activity}</h2>
      <h3>Overall Summary</h3>
      <p>${overallSummary}</p>
      <h3>Page Summaries</h3>
      ${Object.entries(summaries).map(([url, data]) => `
        <div class="summary">
          <h4><a href="${url}" target="_blank">${url}</a></h4>
          <p>${data.summary}</p>
          ${data.memos.length > 0 ? `
            <h5>Memos:</h5>
            <ul>
              ${data.memos.map(memo => `<li class="memo">${memo}</li>`).join('')}
            </ul>
          ` : ''}
        </div>
      `).join('')}
      <h3>Connections</h3>
      <div class="connections">
        <ul>
          ${connections.map(connection => `<li>${connection}</li>`).join('')}
        </ul>
      </div>
    `;
  });
});