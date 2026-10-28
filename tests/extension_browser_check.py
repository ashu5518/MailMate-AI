"""Load the actual unpacked extension against a synthetic Gmail page; no AI calls."""
from pathlib import Path
import tempfile
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
FIXTURE='''<!doctype html><html><body><div class="a3s aiL">Please send the report by tomorrow.</div>
<div contenteditable="true" role="textbox" aria-label="Message Body" g_editable="true">Original Gmail draft.</div></body></html>'''


def main():
    with tempfile.TemporaryDirectory(prefix='mailmate-extension-') as profile, sync_playwright() as p:
        context=p.chromium.launch_persistent_context(profile,channel='chromium',headless=True,
            args=[f'--disable-extensions-except={ROOT / "extension"}',f'--load-extension={ROOT / "extension"}'])
        worker=context.service_workers[0] if context.service_workers else context.wait_for_event('serviceworker')
        extension_id=worker.url.split('/')[2]
        # Fake only provider fetch in the real extension worker.
        worker.evaluate('''() => {globalThis.fetch=async(url,options)=>({ok:true,json:async()=>{
          if(url.endsWith('/health'))return {status:'ok'};
          if(url.endsWith('/proofread'))return {corrected_text:'Thank you.',change_explanations:['Fixed spelling.'],suggestions:[{start:0,end:5,original:'Thnak',replacement:'Thank'}]};
          return {summary:'Report requested.',intent:'Document request',urgency:'Medium',urgency_explanation:'Requested tomorrow.',action_items:['Review request'],deadline_text:'tomorrow',deadline_evidence:'tomorrow',reply:'Thank you for the report request.'};
        }});}''')
        popup=context.new_page();popup.goto(f'chrome-extension://{extension_id}/popup.html')
        expect(popup.locator('#status')).to_have_text('Connected. Open Gmail to get started.')
        assert popup.locator('input').count()==0
        context.route('https://mail.google.com/**',lambda route:route.fulfill(body=FIXTURE,content_type='text/html'))
        page=context.new_page();page.goto('https://mail.google.com/mail/u/0/#inbox/test')
        page.get_by_role('button',name='Open MailMate AI').click()
        page.get_by_role('button',name='Read open email').click()
        expect(page.get_by_label('Received email')).to_have_value('Please send the report by tomorrow.')
        editor=page.get_by_role('textbox',name='Message Body');editor.focus()
        page.get_by_role('button',name='Analyze & Draft',exact=True).click()
        draft=page.get_by_label('Your reply / text to proofread')
        expect(draft).to_have_value('Thank you for the report request.')
        expect(editor).to_have_text('Original Gmail draft.')
        page.get_by_role('button',name='Insert into Gmail').click()
        expect(editor).to_have_text('Thank you for the report request.')
        page.get_by_role('button',name='Undo insertion').click()
        expect(editor).to_have_text('Original Gmail draft.')
        page.get_by_role('button',name='Use Gmail draft').click()
        draft.fill('Thnak you.')
        page.get_by_role('button',name='Fix spelling & grammar').click()
        expect(page.locator('#mailmate-extension #corrected')).to_have_text('Thank you.')
        expect(draft).to_have_value('Thnak you.')
        page.get_by_role('button',name='Use corrected version').click()
        expect(draft).to_have_value('Thank you.')
        editor.fill('Changed outside MailMate.')
        page.get_by_role('button',name='Insert into Gmail').click()
        expect(editor).to_have_text('Changed outside MailMate.')
        expect(page.locator('#mailmate-extension #status')).to_contain_text('draft changed')
        page.get_by_role('button',name='Close MailMate',exact=True).click()
        editor.fill('Thnak you.')
        page.get_by_role('button',name='Check Gmail spelling and grammar').click()
        expect(page.get_by_role('button',name='Replace Thnak with Thank')).to_be_visible()
        expect(editor).to_have_text('Thnak you.')
        assert page.evaluate("CSS.highlights.get('mailmate-spelling').size") > 0
        page.get_by_role('button',name='Replace Thnak with Thank').click()
        expect(editor).to_have_text('Thank you.')
        page.get_by_role('button',name='Undo fixes',exact=True).click()
        expect(editor).to_have_text('Thnak you.')
        page.get_by_role('button',name='Check Gmail spelling and grammar').click()
        expect(page.get_by_role('button',name='Replace Thnak with Thank')).to_be_visible()
        page.get_by_role('button',name='Apply all fixes').click()
        expect(editor).to_have_text('Thank you.')
        (ROOT/'artifacts').mkdir(exist_ok=True)
        page.screenshot(path=str(ROOT/'artifacts'/'extension.png'))
        context.close()
        print('PASS: automatic connection, message capture, drafting, inline spelling fixes, undo, apply all and stale editor protection')


if __name__=='__main__':
    main()
