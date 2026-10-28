const status = document.getElementById('status');
async function checkConnection() {
  const button = document.getElementById('connect'); button.disabled = true;
  try {
    const result = await chrome.runtime.sendMessage({type:'mailmate-request',operation:'health'});
    status.textContent = result.ok ? 'Connected. Open Gmail to get started.' : result.error;
  } catch { status.textContent = 'Unable to connect. Reload the extension and retry.'; }
  finally { button.disabled = false; }
}
document.getElementById('connect').onclick = checkConnection;
checkConnection();
document.getElementById('open').onclick = async () => {
  const [tab] = await chrome.tabs.query({active:true,currentWindow:true});
  if (!tab?.url?.startsWith('https://mail.google.com/')) {
    status.textContent = 'Open Gmail in this tab first.'; return;
  }
  try { await chrome.tabs.sendMessage(tab.id,{type:'mailmate-open'}); window.close(); }
  catch { status.textContent = 'Refresh Gmail after loading the extension, then retry.'; }
};
