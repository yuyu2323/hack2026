import test,{afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import React from 'react';
const dom=new JSDOM('<!doctype html><html><body></body></html>',{url:'http://127.0.0.1:5177/store-owner/submissions/child/compare?store_id=s1'});
Object.assign(globalThis,{window:dom.window,document:dom.window.document,HTMLElement:dom.window.HTMLElement,Event:dom.window.Event,history:dom.window.history});
Object.defineProperty(globalThis,'navigator',{value:dom.window.navigator,configurable:true});
const {render,screen,fireEvent,waitFor,within,cleanup}=await import('@testing-library/react');
const {api,ApiError}=await import('@storeloop/api-client');
const {SessionContext}=await import('../src/shared/ui.tsx');
const {Comparison}=await import('../src/shared/business.tsx');
const original=api.get;
const account={id:'owner',login_id:'test.owner',display_name:'검증 점주',role:'store_owner',region_id:'region',is_active:true,version:1,store_ids:['s1'],permissions:[]};
const side=(id:string,rate:number)=>({submission_id:id,compliance_rate:rate,assessable_rate:100,photos:[{id:id+'-photo',position:1,url:'/api/media/'+id}]});
const comparison={parent:side('parent',60),current:side('child',100),criteria:[{rule_key:'labels',before:'pass',after:'pass',criterion_changed:true,change:'unavailable'},{rule_key:'new_rule',before:null,after:'pass',criterion_changed:true,change:'unavailable'}]};
const parent={id:'parent',created_at:'2026-09-20T23:00:00Z',parent:null,context:{guidelines:[{rule_key:'labels',version:1}]}};
const child={id:'child',created_at:'2026-09-21T01:00:00Z',parent:{id:'parent'},context:{guidelines:[{rule_key:'labels',version:2},{rule_key:'new_rule',version:1}]}};
const mount=()=>render(React.createElement(SessionContext.Provider,{value:{account:account as any,location:window.location.pathname,refreshIdentity:async()=>{},security:()=>{}}},React.createElement(Comparison,{id:'child'})));
afterEach(()=>{cleanup();api.get=original;});

test('기존 상세의 snapshot을 rule_key로 대응해 전후 버전을 표시하고 사진·수치·탐색조건을 유지한다',async()=>{
 const requests:string[]=[];api.get=async(path:string)=>{requests.push(path);return(path.endsWith('/comparison')?comparison:path.endsWith('/parent')?parent:child) as any;};
 mount();await screen.findByText('v2');
 assert.ok(screen.getByRole('columnheader',{name:'이전 기준 버전'}));assert.ok(screen.getByRole('columnheader',{name:'이후 기준 버전'}));
 const row=within(screen.getByText('labels · 기준 변경').closest('tr')!);await row.findByText('v1');assert.ok(row.getByText('v2'));assert.ok(row.getByText('비교 불가'));
 assert.ok(within(screen.getByText('new_rule · 기준 변경').closest('tr')!).getByText('미적용'));
 assert.ok(screen.getByText('준수율 60% · 판단 가능률 100%'));assert.ok(screen.getByText('준수율 100% · 판단 가능률 100%'));
 assert.equal(screen.getByAltText('이전 제출 사진 1').getAttribute('src'),'/api/media/parent');assert.equal(screen.getByAltText('개선 후 제출 사진 1').getAttribute('src'),'/api/media/child');
 assert.equal(screen.getByRole('link',{name:'← 현재 결과로'}).getAttribute('href'),'/store-owner/submissions/child?store_id=s1');
 assert.equal(screen.getByRole('region',{name:'기준별 변화'}).getAttribute('tabindex'),'0');
 assert.deepEqual(requests.sort(),['/submissions/child','/submissions/child/comparison','/submissions/parent']);
});

test('버전 상세 실패를 미적용으로 오해시키지 않으며 명시 재조회 후 실제 버전을 표시한다',async()=>{
 let fails=true;api.get=async(path:string)=>{if(path==='/submissions/parent'){if(fails)throw new ApiError(503,'UNAVAILABLE','이전 버전 조회 실패');return parent as any;}return(path.endsWith('/comparison')?comparison:child) as any;};
 mount();await screen.findByText('이전 버전 조회 실패');
 const row=within(screen.getByText('labels · 기준 변경').closest('tr')!);assert.ok(row.getByText('조회 실패'));assert.ok(row.getByText('v2'));
 fails=false;fireEvent.click(screen.getByRole('button',{name:'다시 조회'}));await waitFor(()=>assert.ok(row.getByText('v1')));assert.equal(screen.queryByText('이전 버전 조회 실패'),null);
});
