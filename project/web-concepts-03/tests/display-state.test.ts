import test,{afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {createElement as h} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
const dom=new JSDOM('<!doctype html><html><body></body></html>',{url:'http://localhost:5175/store-owner/submit'});
for(const name of ['window','document','HTMLElement','HTMLInputElement','HTMLFormElement','Event','CustomEvent','MouseEvent','FormData','File','history','location'])Object.defineProperty(globalThis,name,{value:(dom.window as any)[name],configurable:true,writable:true});
Object.defineProperty(globalThis,'navigator',{value:dom.window.navigator,configurable:true});
const {render,screen,fireEvent,waitFor,cleanup}=await import('@testing-library/react');
const {api,Session,FileImage,ContactSheet}=await import('../src/shared/ui.tsx');
const {Submit}=await import('../src/store-owner/pages.tsx');
const original={get:api.get,error:console.error,create:URL.createObjectURL,revoke:URL.revokeObjectURL};
const account={id:'display-owner',login_id:'synthetic-owner',display_name:'검증 점주',role:'store_owner',region_id:null,is_active:true,version:1,store_ids:[],permissions:['submit']};
const wrap=(child:any)=>h(Session.Provider,{value:account as any},child);
afterEach(()=>{cleanup();api.get=original.get;console.error=original.error;URL.createObjectURL=original.create;URL.revokeObjectURL=original.revoke;});

test('Reference 미리보기는 blob URL 준비 전 이미지 요청을 만들지 않는다',()=>{
  const errors:string[]=[];console.error=(...args:any[])=>errors.push(args.map(String).join(' '));
  const html=renderToStaticMarkup(h(FileImage,{file:new File(['synthetic'],'reference.png',{type:'image/png'}),alt:'검증 Reference'}));
  assert.equal(html.includes('<img'),false,'blob URL 준비 전에는 img를 렌더링하지 않아야 합니다.');
  assert.equal(errors.some(message=>message.includes('empty string')),false);
});

test('점주 사진 선택은 빈 src 경고 없이 blob 이미지를 표시하고 삭제 시 폐기한다',async()=>{
  const errors:string[]=[],revoked:string[]=[];console.error=(...args:any[])=>errors.push(args.map(String).join(' '));
  URL.createObjectURL=()=> 'blob:submission-display-test';URL.revokeObjectURL=url=>revoked.push(url);
  api.get=async()=>({items:[],total:0,page:1,page_size:100}) as any;
  render(wrap(h(Submit)));
  fireEvent.change(screen.getByLabelText(/^제출 사진/),{target:{files:[new File(['synthetic'],'shelf.png',{type:'image/png'})]}});
  await waitFor(()=>assert.equal(screen.getByAltText('제출할 사진 1').getAttribute('src'),'blob:submission-display-test'));
  assert.equal(errors.some(message=>message.includes('empty string')),false,'초기 사진 렌더에 빈 src 경고가 없어야 합니다.');
  fireEvent.click(screen.getByRole('button',{name:'삭제'}));
  assert.equal(screen.queryByAltText('제출할 사진 1'),null);
  assert.deepEqual(revoked,['blob:submission-display-test']);
});

const item=(status:string,review_summary:any=null)=>({id:'display-submission',store_name:'검증 매장',category_name:'음료',created_at:'2026-09-21T00:00:00Z',thumbnail:null,job:{status},review_summary});
test('기술 실패 사진 이력은 대기 대신 운영자 재처리 안내를 표시한다',()=>{
  const html=renderToStaticMarkup(wrap(h(ContactSheet,{items:[item('failed')]})));
  assert.match(html,/운영자.*재처리/);
  assert.doesNotMatch(html,/분석 결과를 기다리고 있어요/);
});

test('처리 중 사진과 완료된 평가는 각각 대기와 결과 수치를 유지한다',()=>{
  for(const status of ['queued','running']){
    const html=renderToStaticMarkup(wrap(h(ContactSheet,{items:[item(status)]})));
    assert.match(html,/분석 결과를 기다리고 있어요/);
    assert.doesNotMatch(html,/재처리/);
  }
  const html=renderToStaticMarkup(wrap(h(ContactSheet,{items:[item('succeeded',{compliance_rate:75,assessable_rate:100,source_kind:'mock'})]})));
  assert.match(html,/준수 75/);assert.match(html,/판단 가능 100/);
  assert.doesNotMatch(html,/분석 결과를 기다리고 있어요|재처리/);
});
