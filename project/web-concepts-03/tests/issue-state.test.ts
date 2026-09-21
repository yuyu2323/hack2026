import test,{afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {createElement as h} from 'react';
const dom=new JSDOM('<!doctype html><html><body></body></html>',{url:'http://localhost:5175/store-owner/issues/i1'});
for(const name of ['window','document','HTMLElement','Event','CustomEvent','FormData','File','history','location'])Object.defineProperty(globalThis,name,{value:(dom.window as any)[name],configurable:true,writable:true});
Object.defineProperty(globalThis,'navigator',{value:dom.window.navigator,configurable:true});
const {render,screen,cleanup}=await import('@testing-library/react');
const {api,Session}=await import('../src/shared/ui.tsx');
const {Issues}=await import('../src/ofc-admin/pages.tsx');
const original=api.get;
const account={id:'issue-owner',login_id:'synthetic-owner',display_name:'검증 점주',role:'store_owner',region_id:null,is_active:true,version:1,store_ids:['s1'],permissions:['submit']};
afterEach(()=>{cleanup();api.get=original;});
for(const [status,heading] of [['resolved','조치가 완료되었습니다.'],['open','OFC의 답변을 기다려 주세요.'],['in_progress','OFC가 확인하고 있습니다.']]){
 test(`점주 ${status} 문의 안내는 실제 조치 상태와 일치하고 관리 권한을 추가하지 않는다`,async()=>{
  const requests:string[]=[];api.get=async(path:string)=>{requests.push(path);return{id:'i1',title:'검증 문의',description:'앞줄 질문',store_name:'검증 매장',category_name:'음료',submission_id:'s1',status,version:2,priority:'normal',assignee_id:'ofc1',assignee_name:'검증 OFC',created_at:'2026-09-21T00:00:00Z',next_check_at:null,resolution:status==='resolved'?'현장 확인 후 해결':null,actions:[{id:'act1',actor_name:'검증 OFC',created_at:'2026-09-21T01:00:00Z',body:'사진 확인했습니다.',to_status:status}]} as any;};
  render(h(Session.Provider,{value:account as any},h(Issues,{id:'i1'})));
  await screen.findByRole('heading',{name:heading});
  if(status!=='open')assert.equal(screen.queryByRole('heading',{name:'OFC의 답변을 기다려 주세요.'}),null);
  if(status==='resolved')assert.ok(screen.getByText('해결 내용: 현장 확인 후 해결'));
  assert.ok(screen.getByText('사진 확인했습니다.'));assert.ok(screen.getByRole('link',{name:'연결된 사진과 근거 ↗'}));
  assert.equal(screen.queryByRole('button',{name:'조치 변경 저장'}),null);
  assert.equal(screen.queryByLabelText('상태'),null);
  assert.deepEqual(requests,['/issues','/issues/i1']);
 });
}
