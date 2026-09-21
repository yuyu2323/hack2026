import test,{afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {createElement as h} from 'react';
const dom=new JSDOM('<!doctype html><html><body></body></html>',{url:'http://localhost:5175/ofc-admin?store_id=store1&category_id=cat1&date_from=2026-09-01'});
for(const name of ['window','document','HTMLElement','HTMLInputElement','HTMLFormElement','Event','CustomEvent','MouseEvent','FormData','File','history','location'])Object.defineProperty(globalThis,name,{value:(dom.window as any)[name],configurable:true,writable:true});
Object.defineProperty(globalThis,'navigator',{value:dom.window.navigator,configurable:true});
const {render,screen,fireEvent,waitFor,cleanup}=await import('@testing-library/react');
const {api,Session}=await import('../src/shared/ui.tsx');
const {Dashboard,Guidelines}=await import('../src/ofc-admin/pages.tsx');
const original={get:api.get,patch:api.patch,post:api.post};
const account={id:'display-hq',login_id:'synthetic-hq',display_name:'검증 본사',role:'hq',region_id:null,is_active:true,version:1,store_ids:[],permissions:[]};
const page=(items:any[])=>({items,total:items.length,page:1,page_size:100});
const wrap=(child:any)=>h(Session.Provider,{value:account as any},child);
const filters={store_id:'store1',category_id:'cat1',date_from:'2026-09-01',is_active:true};
const dashboard={kpis:{store_count:1,submission_count:1,succeeded_count:1,failed_count:0,needs_ofc_review_count:0,open_issue_count:1,compliance_rate:80,assessable_rate:100},sample_count:1,mock_review_count:1,filters,stores:[{store_id:'store1',store_name:'검증 매장',status:'evaluated',submission_count:1,open_issue_count:1,compliance_rate:80,assessable_rate:100,drilldown:filters}]};
afterEach(()=>{cleanup();api.get=original.get;api.patch=original.patch;api.post=original.post;history.replaceState({},'','/ofc-admin?store_id=store1&category_id=cat1&date_from=2026-09-01')});

test('영업 홈은 사진을 보조 집계와 매장 목록보다 먼저 제공하며 같은 범위를 drilldown한다',async()=>{
  const requests:string[]=[];
  api.get=async(path:string)=>{requests.push(path);if(path.startsWith('/dashboard'))return dashboard as any;if(path.startsWith('/submissions'))return page([{id:'submission1',store_name:'검증 매장',category_name:'음료',created_at:'2026-09-21T00:00:00Z',thumbnail:{url:'/api/media/synthetic-photo'},job:{status:'succeeded'},review_summary:{compliance_rate:80,assessable_rate:100,source_kind:'mock'}}]) as any;return page([{id:path.startsWith('/stores')?'store1':path.startsWith('/categories')?'cat1':'region1',name:'검증 범위'}]) as any;};
  render(wrap(h(Dashboard)));
  const photo=await screen.findByAltText('검증 매장 음료 제출 사진');
  const sample=await screen.findByText(/평가 표본 1개/);
  assert.ok(photo.compareDocumentPosition(sample)&dom.window.Node.DOCUMENT_POSITION_FOLLOWING,'처음 읽는 주정보는 집계보다 사진이어야 합니다.');
  const store=screen.getByRole('link',{name:/평가 완료 검증 매장 제출 1/});
  assert.ok(photo.compareDocumentPosition(store)&dom.window.Node.DOCUMENT_POSITION_FOLLOWING);
  for(const name of ['매장','카테고리','시작일 (UTC)','종료일 (UTC)'])assert.ok(screen.getByLabelText(name));
  for(const [name,path,extra] of [[/평가 완료 검증 매장 제출 1/,'/ofc-admin/submissions',{}],['이 범위의 미해결 조치 보기','/ofc-admin/issues',{unresolved:'true'}],['기술 실패 보기','/ofc-admin/submissions',{status:'failed'}]] as const){
    const url=new URL(screen.getByRole('link',{name}).getAttribute('href')!,'http://localhost');
    assert.equal(url.pathname,path);
    for(const [key,value] of Object.entries({...filters,...extra}))assert.equal(url.searchParams.get(key),String(value));
  }
  assert.equal(screen.getByRole('link',{name:'지표·매장 현황 ↓'}).getAttribute('href'),'#dashboard-status');
  for(const base of ['/dashboard','/submissions']){const url=new URL(requests.find(path=>path.startsWith(base))!,'http://localhost');assert.equal(url.searchParams.get('category_id'),'cat1');assert.equal(url.searchParams.get('store_id'),'store1');assert.equal(url.searchParams.get('date_from'),'2026-09-01');}
});

test('비활성화로 상태 버전이 커져도 내용 버전을 표시하고 활성화 요청은 상태 버전을 보낸다',async()=>{
  history.replaceState({},'','/ofc-admin/guidelines/g1');
  const current={id:'g1',rule_key:'facing',title:'검증 기준',level:'HQ',is_active:false,version:4,current_version:2,current:{version_id:'v2',version:2,text:'앞줄을 정렬합니다.'}};
  const changes:any[]=[];
  api.get=async(path:string)=>path==='/guidelines/g1'?current as any:path.includes('/versions')?page([{version_id:'v2',version:2,text:'앞줄을 정렬합니다.',created_at:'2026-09-21T00:00:00Z',change_reason:'내용 개선'}]) as any:page([]) as any;
  api.patch=async(path:string,body:any)=>{changes.push({path,body});return current as any;};
  render(wrap(h(Guidelines,{id:'g1'})));
  await screen.findByLabelText('변경 사유');
  assert.ok(screen.getByText('현재 기준 v2'));
  assert.equal(screen.queryByText('현재 저장 버전 4'),null);
  fireEvent.change(screen.getByLabelText('변경 사유'),{target:{value:'검토 후 재활성화'}});
  fireEvent.click(screen.getByRole('button',{name:'기준 활성화'}));
  await waitFor(()=>assert.equal(changes.length,1));
  assert.deepEqual(changes[0],{path:'/guidelines/g1',body:{version:4,is_active:true,reason:'검토 후 재활성화'}});
});
