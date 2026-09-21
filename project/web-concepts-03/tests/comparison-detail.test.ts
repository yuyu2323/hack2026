import test,{afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {createElement as h} from 'react';
const dom=new JSDOM('<!doctype html><html><body></body></html>',{url:'http://localhost:5175/store-owner/submissions/child/compare'});
for(const name of ['window','document','HTMLElement','Event','CustomEvent','MouseEvent','FormData','File','history','location'])Object.defineProperty(globalThis,name,{value:(dom.window as any)[name],configurable:true,writable:true});
Object.defineProperty(globalThis,'navigator',{value:dom.window.navigator,configurable:true});
const {render,screen,fireEvent,waitFor,cleanup,within}=await import('@testing-library/react');
const {api,ApiError,Session}=await import('../src/shared/ui.tsx');
const {Comparison}=await import('../src/store-owner/pages.tsx');
const original=api.get;
const account={id:'compare-owner',login_id:'synthetic-owner',display_name:'검증 점주',role:'store_owner',region_id:null,is_active:true,version:1,store_ids:['s1'],permissions:['submit']};
const side=(id:string,rate:number)=>({submission_id:id,review_id:id+'-review',compliance_rate:rate,assessable_rate:100,photos:[{id:id+'-photo',position:1,url:'/api/media/'+id}]});
const comparison={parent:side('parent',60),current:side('child',100),criteria:[{rule_key:'facing',before:'fail',after:'pass',criterion_changed:false,change:'resolved'},{rule_key:'labels',before:'pass',after:'pass',criterion_changed:true,change:'unavailable'},{rule_key:'new_rule',before:null,after:'pass',criterion_changed:true,change:'unavailable'}],narrative:'검증 비교 설명'};
const parent={id:'parent',created_at:'2026-09-20T23:00:00Z',context:{guidelines:[{rule_key:'facing',version:1},{rule_key:'labels',version:1}]}};
const child={id:'child',created_at:'2026-09-21T01:00:00Z',context:{guidelines:[{rule_key:'facing',version:1},{rule_key:'labels',version:2},{rule_key:'new_rule',version:1}]}};
const wrap=()=>h(Session.Provider,{value:account as any},h(Comparison,{id:'child'}));
afterEach(()=>{cleanup();api.get=original;});

test('비교는 각 제출 일시와 snapshot 기준 버전을 표시하고 원본 사진·점수·변경 제한을 보존한다',async()=>{
 const calls:string[]=[];api.get=async(path:string)=>{calls.push(path);return(path.endsWith('/comparison')?comparison:path==='/submissions/parent'?parent:child) as any;};
 const {container}=render(wrap());
 await screen.findByAltText('현재 사진 1');
 await waitFor(()=>assert.equal(container.querySelectorAll('time').length,2));
 assert.deepEqual([...container.querySelectorAll('time')].map(el=>el.getAttribute('datetime')),[parent.created_at,child.created_at]);
 assert.ok([...container.querySelectorAll('time')].every(el=>el.textContent?.includes('2026')&&el.textContent?.includes('KST')));
 assert.ok(screen.getByRole('columnheader',{name:'이전 기준 버전'}));assert.ok(screen.getByRole('columnheader',{name:'현재 기준 버전'}));
 const labels=within(screen.getByText('labels').closest('tr')!);assert.ok(labels.getByText('v1'));assert.ok(labels.getByText('v2'));assert.ok(labels.getByText('기준 변경 · 비교 불가'));
 const added=within(screen.getByText('new_rule').closest('tr')!);assert.ok(added.getByText('미적용'));assert.ok(added.getByText('v1'));
 assert.equal(screen.getByAltText('이전 사진 1').getAttribute('src'),'/api/media/parent');assert.equal(screen.getByAltText('현재 사진 1').getAttribute('src'),'/api/media/child');
 assert.ok(screen.getByText('준수 60% · 판단 가능 100%'));assert.ok(screen.getByText('준수 100% · 판단 가능 100%'));
 assert.equal(screen.getByRole('region',{name:'기준별 변화'}).getAttribute('tabindex'),'0');
 assert.deepEqual(calls.sort(),['/submissions/child','/submissions/child/comparison','/submissions/parent']);
});

test('상세 조회 실패는 버전을 추정하지 않고 사진과 점수를 보존하며 명시 재조회로 회복한다',async()=>{
 let failed=true;api.get=async(path:string)=>{if(path==='/submissions/parent'){if(failed)throw new ApiError(503,'UNAVAILABLE','이전 제출 정보 조회 실패');return parent as any;}return(path.endsWith('/comparison')?comparison:child) as any;};
 render(wrap());await screen.findByText('이전 제출 정보 조회 실패');
 const labels=within(screen.getByText('labels').closest('tr')!);assert.ok(labels.getByText('조회 실패'));assert.ok(labels.getByText('v2'));
 assert.ok(screen.getByAltText('이전 사진 1'));assert.ok(screen.getByText('준수 60% · 판단 가능 100%'));
 failed=false;fireEvent.click(screen.getByRole('button',{name:'최신 정보 다시 읽기'}));
 await waitFor(()=>assert.ok(labels.getByText('v1')));assert.equal(screen.queryByText('이전 제출 정보 조회 실패'),null);
});

test('이전 제출이 없으면 빈 비교 안내만 제공하고 추가 상세를 요청하지 않는다',async()=>{
 const calls:string[]=[];api.get=async(path:string)=>{calls.push(path);return{...comparison,parent:null,criteria:[]} as any;};
 render(wrap());await screen.findByText('이전 제출이 연결되지 않은 사진입니다.');assert.deepEqual(calls,['/submissions/child/comparison']);
});
