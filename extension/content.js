(() => {
  if (document.getElementById('mailmate-extension')) return;
  const host = document.createElement('div'); host.id = 'mailmate-extension';
  const root = host.attachShadow({mode:'open'});
  root.innerHTML = `
  <style>
    :host{all:initial;font:14px/1.5 system-ui;color:#172033}
    *{box-sizing:border-box}button,input,textarea,select{font:inherit}
    button{cursor:pointer;border:1px solid #dce3e1;border-radius:9px;padding:9px 12px;background:white;color:#172033}
    button:disabled{opacity:.45;cursor:default}button:hover:not(:disabled){background:#eef6f3}
    .primary{background:#0f766e;color:white;border-color:#0f766e}.primary:hover:not(:disabled){background:#115e59}
    button:focus-visible,textarea:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid #0f766e;outline-offset:2px}
    #launch{position:fixed;right:24px;bottom:24px;z-index:2147483646;background:#0f766e;color:white;box-shadow:0 4px 20px #17203330;border:0;border-radius:30px;padding:13px 20px;font-weight:650}
    #panel{position:fixed;right:16px;top:16px;bottom:16px;width:390px;max-width:calc(100vw - 32px);z-index:2147483647;background:#f5f7f8;border:1px solid #dce3e1;border-radius:18px;box-shadow:0 12px 60px #17203330;overflow:auto;padding:20px}
    [hidden]{display:none!important}.top{display:flex;justify-content:space-between;align-items:center}.brand{font-size:21px;font-weight:750;color:#0f766e}
    .hint{font-size:12px;color:#64748b;margin:8px 0 16px}.row{display:flex;gap:8px}.row>*{flex:1;min-width:0}
    label{display:block;font-size:12px;font-weight:650;margin:12px 0 5px}
    textarea,input,select{display:block;width:100%;background:white;border:1px solid #dce3e1;border-radius:9px;padding:10px;color:#172033}
    textarea{resize:vertical;line-height:1.6}#email{height:125px}#instructions{height:65px}#draft{height:180px}
    .actions{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.card{background:white;padding:14px;border:1px solid #e2e8ed;border-radius:12px;margin:12px 0}
    h3{margin:0 0 6px;font-size:14px}.detail{white-space:pre-wrap;font-size:13px;margin:8px 0}
    #status{white-space:pre-wrap;color:#0f766e;font-size:12px;margin:10px 0}#status.error{color:#b91c1c}
    #corrected{white-space:pre-wrap;font-size:13px}.changes{font-size:12px;color:#64748b}
  </style>
  <button id="launch" aria-label="Open MailMate AI">✉ MailMate</button>
  <section id="panel" aria-label="MailMate writing assistant" hidden>
    <div class="top"><span class="brand">✉ MailMate AI</span><button id="close" aria-label="Close MailMate">✕</button></div>
    <p class="hint">Understand the message. Make the reply yours.</p>
    <div class="row"><button id="read">Read open email</button><button id="useDraft">Use Gmail draft</button></div>
    <label for="email">Received email</label><textarea id="email" placeholder="Read the open email or paste it here."></textarea>
    <label for="instructions">Reply instructions (optional)</label><textarea id="instructions" placeholder="Ask for more time, decline politely…"></textarea>
    <div class="row"><div><label for="tone">Tone</label><select id="tone"><option>Professional</option><option>Friendly</option><option>Formal</option><option>Casual</option><option>Polite</option></select></div>
    <div><label for="length">Length</label><select id="length"><option>Short</option><option>Medium</option><option>Detailed</option></select></div></div>
    <label for="signature">Signature (optional)</label><input id="signature" maxlength="500" placeholder="Your name">
    <div class="actions"><button id="analyze" class="primary">Analyze & Draft</button><button id="regenerate">Regenerate</button></div>
    <div id="insights" class="card" hidden><h3>Email insights</h3><div id="summary" class="detail"></div><div id="meta" class="detail"></div><div id="actions" class="detail"></div><div id="deadline" class="detail"></div></div>
    <label for="draft">Your reply / text to proofread</label><textarea id="draft" placeholder="Your suggested reply appears here. You can also paste text to proofread."></textarea>
    <div class="actions"><button id="proofread">Fix spelling & grammar</button><button id="copy">Copy</button></div>
    <div id="proof" class="card" hidden><h3>Suggested correction</h3><div id="corrected"></div><p id="changes" class="changes"></p><button id="accept">Use corrected version</button></div>
    <div class="actions"><button id="insert" class="primary">Insert into Gmail</button><button id="undo" disabled>Undo insertion</button><button id="clear">Clear</button></div>
    <div id="status" role="status" aria-live="polite"></div>
  </section>`;
  document.documentElement.append(host);
  const $ = id => root.getElementById(id);
  let editor = null, busy = false, outputTarget = null, undo = null;
  let analyzedEmail = null, proofOriginal = null, correction = null;
  const visible = el => el.isConnected && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  const isEditor = el => el?.matches('[contenteditable="true"][role="textbox"], [contenteditable="true"][g_editable="true"]');
  document.addEventListener('focusin', event => {
    const found = event.target.closest?.('[contenteditable="true"]');
    if (isEditor(found) && visible(found)) editor = found;
  });
  function status(text, error=false) { $('status').textContent=text; $('status').classList.toggle('error',error); }
  function open() { $('panel').hidden=false; $('launch').hidden=true; $('email').focus(); }
  $('launch').onclick=open;
  $('close').onclick=()=>{$('panel').hidden=true;$('launch').hidden=false;};
  root.addEventListener('keydown', e=>{if(e.key==='Escape') $('close').click();});
  chrome.runtime.onMessage.addListener(msg=>{if(msg?.type==='mailmate-open')open();});
  function currentEditor() {
    if (editor && visible(editor)) return editor;
    const found=[...document.querySelectorAll('[contenteditable="true"]')].filter(el=>isEditor(el)&&visible(el));
    if(found.length===1) {editor=found[0];return editor;}
    throw new Error(found.length ? 'Click inside the Gmail draft you want to use, then try again.' : 'Open a Gmail reply or compose window first.');
  }
  function readEmail() {
    const messages=[...document.querySelectorAll('.a3s.aiL, .a3s')].filter(visible);
    if(!messages.length) throw new Error('Open an email conversation or paste the email manually.');
    // Use the last visible message, not the full inbox or hidden messages.
    const text=messages.at(-1).innerText;
    if(!text.trim())throw new Error('This message has no readable text. Paste it manually.');
    $('email').value=text;
    status('Open message loaded. Review it before analyzing.');
  }
  $('read').onclick=()=>{try{readEmail();}catch(e){status(e.message,true);}};
  $('useDraft').onclick=()=>{try{const target=currentEditor();$('draft').value=target.innerText;outputTarget={editor:target,original:target.innerText};$('proof').hidden=true;status('Gmail draft loaded.');}catch(e){status(e.message,true);}};
  function payload(){return {email:$('email').value,instructions:$('instructions').value,signature:$('signature').value,tone:$('tone').value,length:$('length').value};}
  function validate(text,limit,label){if(!text.trim())throw new Error(`Enter ${label} first.`);if(text.length>limit)throw new Error(`${label} exceeds ${limit.toLocaleString()} characters. Shorten it first.`);}
  async function request(operation) {
    if(busy)return;
    try {
      let data;
      if(operation==='proofread'){validate($('draft').value,20000,'text');data={text:$('draft').value};}
      else {data=payload();validate(data.email,20000,'email');if(data.instructions.length>2000)throw new Error('Reply instructions exceed 2,000 characters.');}
      let target=null;try{const e=currentEditor();target={editor:e,original:e.innerText};}catch{}
      busy=true;
      root.querySelectorAll('button:not(#close),textarea,input,select').forEach(el=>el.disabled=true);
      status('Working on your text…');
      const result=await chrome.runtime.sendMessage({type:'mailmate-request',operation,payload:data});
      if(!result?.ok)throw new Error(result?.error||'Reload Gmail and retry.');
      if(operation==='proofread') {
        proofOriginal=data.text;correction=result.data.corrected_text;
        $('corrected').textContent=correction;
        $('changes').textContent=result.data.change_explanations.join('\n')||'No corrections needed.';
        $('proof').hidden=false;
      } else {
        $('draft').value=result.data.reply;outputTarget=target;$('proof').hidden=true;
        if(operation==='analyze') {
          analyzedEmail=data.email;
          $('summary').textContent=result.data.summary;
          $('meta').textContent=`${result.data.intent} · ${result.data.urgency} urgency\n${result.data.urgency_explanation}`;
          $('actions').textContent=result.data.action_items.map(x=>'• '+x).join('\n')||'No explicit action requested.';
          $('deadline').textContent='Deadline: '+(result.data.deadline_text||'Not specified')+(result.data.deadline_evidence?'\nSource: '+result.data.deadline_evidence:'');
          $('insights').hidden=false;
        }
      }
      status('Ready. Review the result before inserting it.');
    }catch(e){status(e.message||'Unable to complete this request.',true);}
    finally {busy=false;root.querySelectorAll('button,textarea,input,select').forEach(el=>el.disabled=false);$('undo').disabled=!undo;}
  }
  $('analyze').onclick=()=>request('analyze');$('regenerate').onclick=()=>request('reply');$('proofread').onclick=()=>request('proofread');
  $('email').oninput=()=>{if(analyzedEmail!==null&&analyzedEmail!==$('email').value)status('Insights belong to an earlier email. Analyze again to update them.');};
  $('draft').oninput=()=>{if(proofOriginal!==null&&proofOriginal!==$('draft').value){$('accept').disabled=true;status('Text changed. Proofread again to refresh corrections.');}};
  $('accept').onclick=()=>{if($('draft').value!==proofOriginal){status('Text changed. Proofread again.',true);return;}$('draft').value=correction;$('proof').hidden=true;status('Correction applied to the preview.');};
  $('copy').onclick=async()=>{try{await navigator.clipboard.writeText($('draft').value);status('Reply copied.');}catch{status('Select the preview text and copy it manually.',true);}};
  function replace(target,text){
    target.focus();const selection=window.getSelection(),range=document.createRange();
    range.selectNodeContents(target);selection.removeAllRanges();selection.addRange(range);
    if(!document.execCommand('insertText',false,text))throw new Error('Could not insert into this editor. Copy the draft and paste it manually.');
    target.dispatchEvent(new Event('input',{bubbles:true}));
  }
  $('insert').onclick=()=>{
    try {
      validate($('draft').value,20000,'reply');
      const target=currentEditor();
      if(outputTarget&&(target!==outputTarget.editor||target.innerText!==outputTarget.original))throw new Error('The Gmail draft changed or another editor is selected. Load it again with Use Gmail draft before replacing it.');
      const previous=target.innerText;
      replace(target,$('draft').value);
      undo={editor:target,previous,inserted:target.innerText};outputTarget={editor:target,original:target.innerText};$('undo').disabled=false;
      status('Inserted into Gmail. Review before sending.');
    }catch(e){status(e.message,true);}
  };
  $('undo').onclick=()=>{
    try{if(!undo||!visible(undo.editor)||undo.editor.innerText!==undo.inserted)throw new Error('The draft changed after insertion. Use Gmail’s undo or edit it manually.');
      replace(undo.editor,undo.previous);outputTarget={editor:undo.editor,original:undo.editor.innerText};undo=null;$('undo').disabled=true;status('Previous draft restored.');
    }catch(e){status(e.message,true);}
  };
  $('clear').onclick=()=>{for(const id of ['email','instructions','draft'])$(id).value='';$('insights').hidden=true;$('proof').hidden=true;analyzedEmail=null;proofOriginal=null;correction=null;outputTarget=null;status('Workspace cleared.');};
})();
