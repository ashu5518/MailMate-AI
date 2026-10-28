(() => {
  if(document.getElementById('mailmate-inline'))return;
  const host=document.createElement('div');host.id='mailmate-inline';
  const root=host.attachShadow({mode:'open'});
  root.innerHTML=`<style>
    :host{all:initial;font:13px/1.5 system-ui;color:#172033}*{box-sizing:border-box}
    [hidden]{display:none!important}button{font:inherit;cursor:pointer;border:1px solid #dce3e1;border-radius:9px;background:white;color:#172033;padding:8px 12px}
    button:focus-visible{outline:2px solid #0f766e;outline-offset:2px}button:disabled{opacity:.5}
    #check{position:fixed;z-index:2147483646;box-shadow:0 2px 10px #17203318;border-radius:20px;color:#0f766e;background:#f0faf6;font-weight:650;padding:6px 12px}
    #suggestions{position:fixed;z-index:2147483647;width:300px;max-width:calc(100vw - 24px);background:white;border:1px solid #dce3e1;box-shadow:0 8px 30px #17203325;border-radius:14px;padding:15px;max-height:360px;overflow:auto}
    .top{display:flex;justify-content:space-between;align-items:center;font-weight:700;color:#0f766e}.top button{border:0;padding:3px 8px}
    #message{font-size:12px;color:#64748b;margin:10px 0;white-space:pre-wrap}#list button{display:block;text-align:left;width:100%;margin:7px 0;background:#f5faf7}
    #all{background:#0f766e;color:white;border:0}#undo{margin-left:6px}.old{color:#b91c1c;text-decoration:line-through}.new{color:#0f766e;font-weight:650}
  </style><button id="check" hidden aria-label="Check Gmail spelling and grammar">✦ Check writing</button>
  <section id="suggestions" hidden aria-label="Inline writing suggestions"><div class="top">MailMate writing check<button id="close" aria-label="Close suggestions">✕</button></div>
  <div id="message" role="status" aria-live="polite"></div><div id="list"></div><button id="all" hidden>Apply all fixes</button><button id="undo" hidden>Undo fixes</button></section>`;
  document.documentElement.append(host);
  const style=document.createElement('style');
  style.textContent='::highlight(mailmate-spelling){text-decoration-line:underline;text-decoration-style:wavy;text-decoration-color:#e14949;text-decoration-thickness:1.5px;}';
  document.documentElement.append(style);
  const $=id=>root.getElementById(id);
  const states=new WeakMap();let editor=null,checking=false,requestVersion=0,undo=null;
  const isEditor=el=>el?.matches('[contenteditable="true"][role="textbox"], [contenteditable="true"][g_editable="true"]');
  const visible=el=>el?.isConnected&&el.getClientRects().length>0;
  function position(){
    if(!visible(editor)){$('check').hidden=true;$('suggestions').hidden=true;return;}
    const box=editor.getBoundingClientRect();
    $('check').hidden=!editor.innerText.trim();
    $('check').style.left=Math.max(12,Math.min(box.right-140,window.innerWidth-160))+'px';
    $('check').style.top=Math.max(12,Math.min(box.top+6,window.innerHeight-44))+'px';
    $('suggestions').style.left=Math.max(12,Math.min(box.right-300,window.innerWidth-312))+'px';
    $('suggestions').style.top=Math.max(12,Math.min(box.top+40,window.innerHeight-375))+'px';
  }
  function ranges(state){
    const walker=document.createTreeWalker(editor,NodeFilter.SHOW_TEXT),nodes=[];let node,cursor=0;
    while((node=walker.nextNode())){
      const at=state.source.indexOf(node.data,cursor);
      if(at>=0){nodes.push({node,start:at,end:at+node.data.length});cursor=at+node.data.length;}
    }
    state.edits.forEach(edit=>{
      edit.range=null;if(edit.start===edit.end)return;
      const first=nodes.find(n=>n.start<=edit.start&&n.end>edit.start);
      const last=nodes.find(n=>n.start<edit.end&&n.end>=edit.end);
      if(!first||!last)return;
      const range=document.createRange();range.setStart(first.node,edit.start-first.start);range.setEnd(last.node,edit.end-last.start);
      if(range.toString()===edit.original)edit.range=range;
    });
    if(globalThis.CSS?.highlights&&globalThis.Highlight){
      CSS.highlights.set('mailmate-spelling',new Highlight(...state.edits.filter(e=>e.range).map(e=>e.range)));
    }
  }
  function clearHighlights(){if(globalThis.CSS?.highlights)CSS.highlights.delete('mailmate-spelling');}
  function showMessage(message){$('suggestions').hidden=false;$('message').textContent=message;position();}
  function render(){
    const state=states.get(editor);$('list').replaceChildren();$('all').hidden=true;$('undo').hidden=!undo;
    if(!state||state.source!==editor.innerText)return;
    ranges(state);
    $('check').textContent=state.edits.length?`✦ ${state.edits.length} writing fixes`:'✓ Looks good';
    showMessage(state.edits.length?'Click an underlined word or choose a correction below.':'No spelling or grammar corrections found.');
    state.edits.forEach(edit=>{
      const button=document.createElement('button');
      const old=document.createElement('span');old.className='old';old.textContent=edit.original||'(insert)';
      const next=document.createElement('span');next.className='new';next.textContent=edit.replacement||'(remove)';
      button.append(old,document.createTextNode(' → '),next);
      button.setAttribute('aria-label',`Replace ${edit.original||'missing text'} with ${edit.replacement||'nothing'}`);
      button.onclick=()=>apply(edit);$('list').append(button);
    });
    $('all').hidden=!state.edits.length;
  }
  function focusEditor(next){
    if(editor!==next){requestVersion++;clearHighlights();$('suggestions').hidden=true;editor=next;}
    position();const state=states.get(editor);if(state&&state.source===editor.innerText){ranges(state);$('check').textContent=state.edits.length?`✦ ${state.edits.length} writing fixes`:'✓ Looks good';}
    else $('check').textContent='✦ Check writing';
  }
  document.addEventListener('focusin',event=>{const next=event.target.closest?.('[contenteditable="true"]');if(isEditor(next))focusEditor(next);});
  document.addEventListener('input',event=>{
    const next=event.target.closest?.('[contenteditable="true"]');if(!isEditor(next))return;
    focusEditor(next);states.delete(next);requestVersion++;clearHighlights();$('check').textContent='✦ Check writing';$('suggestions').hidden=true;position();
  });
  document.addEventListener('click',event=>{
    if(!editor?.contains(event.target))return;
    const state=states.get(editor);if(!state||state.source!==editor.innerText)return;
    if(state.edits.some(edit=>edit.range&&[...edit.range.getClientRects()].some(r=>event.clientX>=r.left-3&&event.clientX<=r.right+3&&event.clientY>=r.top&&event.clientY<=r.bottom)))render();
  });
  window.addEventListener('resize',position);document.addEventListener('scroll',position,true);
  new MutationObserver(()=>{if(editor&&!visible(editor)){clearHighlights();position();}}).observe(document.body,{childList:true,subtree:true});
  $('close').onclick=()=>{$('suggestions').hidden=true;};
  root.addEventListener('keydown',event=>{if(event.key==='Escape')$('close').click();});
  $('check').onclick=async()=>{
    if(checking||!visible(editor))return;
    const existing=states.get(editor);if(existing&&existing.source===editor.innerText){render();return;}
    const target=editor,source=editor.innerText,version=++requestVersion;
    if(source.length>20000){showMessage('Draft exceeds 20,000 characters. Shorten it first.');return;}
    checking=true;$('check').disabled=true;$('check').textContent='Checking…';$('list').replaceChildren();$('all').hidden=true;showMessage('Checking spelling and grammar…');
    try{
      const result=await chrome.runtime.sendMessage({type:'mailmate-request',operation:'proofread',payload:{text:source}});
      if(!result?.ok)throw new Error(result?.error||'Reload Gmail and retry.');
      if(version!==requestVersion||target!==editor||target.innerText!==source){showMessage('Draft changed while checking. Click Check writing again.');return;}
      states.set(target,{source,corrected:result.data.corrected_text,edits:result.data.suggestions||[]});render();
    }catch(error){showMessage(error.message||'Unable to check writing. Retry.');}
    finally{checking=false;$('check').disabled=false;if(!states.has(editor))$('check').textContent='✦ Check writing';}
  };
  function replace(range,text){editor.focus();const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);
    if(!document.execCommand('insertText',false,text))throw new Error('Gmail could not apply this fix. Try copying the suggestion.');}
  function apply(edit){
    const state=states.get(editor);if(!state||state.source!==editor.innerText){showMessage('Draft changed. Check writing again.');return;}
    try{
      const previous=editor.innerText;
      if(!edit.range){showMessage('Use Apply all fixes for this correction.');return;}
      const remaining=state.edits.filter(e=>e!==edit).map(e=>({...e,range:null,
        start:e.start>edit.start?e.start+edit.replacement.length-(edit.end-edit.start):e.start,
        end:e.start>edit.start?e.end+edit.replacement.length-(edit.end-edit.start):e.end}));
      replace(edit.range,edit.replacement);
      undo={editor,previous,after:editor.innerText};
      states.set(editor,{source:editor.innerText,corrected:state.corrected,edits:remaining});render();
    }catch(error){showMessage(error.message);}
  }
  $('all').onclick=()=>{
    const state=states.get(editor);if(!state||state.source!==editor.innerText){showMessage('Draft changed. Check writing again.');return;}
    try{const previous=editor.innerText;const range=document.createRange();range.selectNodeContents(editor);replace(range,state.corrected);
      undo={editor,previous,after:editor.innerText};states.set(editor,{source:editor.innerText,corrected:editor.innerText,edits:[]});render();
    }catch(error){showMessage(error.message);}
  };
  $('undo').onclick=()=>{
    if(!undo||undo.editor!==editor||editor.innerText!==undo.after){showMessage('Draft changed after the fix. Use Gmail’s undo instead.');return;}
    try{const previous=undo.previous;const range=document.createRange();range.selectNodeContents(editor);replace(range,previous);undo=null;states.delete(editor);clearHighlights();$('list').replaceChildren();$('all').hidden=true;$('undo').hidden=true;$('check').textContent='✦ Check writing';showMessage('Previous text restored.');}
    catch(error){showMessage(error.message);}
  };
})();
