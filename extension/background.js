const BASE = 'http://127.0.0.1:8765';
chrome.runtime.onMessage.addListener((message, sender, respond) => {
  const ownPage = sender.id === chrome.runtime.id && sender.url?.startsWith(chrome.runtime.getURL(''));
  const gmail = sender.id === chrome.runtime.id && sender.tab?.url?.startsWith('https://mail.google.com/');
  if ((!ownPage && !gmail) || message?.type !== 'mailmate-request') return;
  const paths = {health:'/health', analyze:'/analyze', reply:'/reply', proofread:'/proofread'};
  if (!Object.hasOwn(paths, message.operation)) {
    respond({ok:false,error:'Unknown action.'}); return;
  }
  (async () => {
    try {
      const response = await fetch(BASE + paths[message.operation], {
        method: message.operation === 'health' ? 'GET' : 'POST',
        headers: {'Content-Type':'application/json','X-MailMate-Extension':chrome.runtime.id},
        body: message.operation === 'health' ? undefined : JSON.stringify(message.payload),
        signal: AbortSignal.timeout(70000)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Unable to complete this request.');
      respond({ok:true,data});
    } catch (e) {
      const error = e.name === 'TimeoutError' ? 'The assistant timed out. Retry.' :
        e instanceof TypeError ? 'Local assistant is offline. Start run-extension.ps1 and retry.' : e.message;
      respond({ok:false,error});
    }
  })();
  return true;
});
