import React from 'react';
import {afterEach,it,expect,vi} from 'vitest';
import {cleanup,render,screen,within} from '@testing-library/react';
import {MemoryRouter} from 'react-router-dom';
import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import {api} from '@storeloop/api-client';
import {SessionProvider} from '../src/app/session';
import {Analytics} from '../src/ofc-admin/Analytics';
vi.mock('recharts',()=>Object.fromEntries(['LineChart','Line','XAxis','YAxis','CartesianGrid','Tooltip','ResponsiveContainer','ScatterChart','Scatter'].map(name=>[name,({children}:{children?:React.ReactNode})=><div>{children}</div>])));
afterEach(()=>{cleanup();vi.restoreAllMocks();});
function setup(missing=false){
 const calls=vi.spyOn(api,'get').mockImplementation(async(path:string)=>{
  const [base,query]=path.split('?');const page=new URLSearchParams(query).get('page');
  if(base==='/analytics/trends')return {points:[]};
  if(base==='/analytics/correlation')return {n:1,r:null,reason:'insufficient_samples',excluded_missing_count:0,excluded_unassessable_count:0,points:[{store_id:'store-bank',category_id:'category-snack',week_start:'2026-09-14',compliance_rate:20,sales_amount:50000,review_count:1}]};
  if(base==='/analytics/report')return {group_by:'store',rows:[{id:'store-bank',name:'store-bank',submission_count:1,review_count:1,failed_count:0,open_issue_count:0,compliance_rate:20,assessable_rate:100,mock_sales_amount:50000}]};
  const items=missing?[]:base==='/stores'?(page==='2'?[{id:'store-bank',name:'은행길점'}]:[{id:'other',name:'다른 매장'}]):base==='/categories'?[{id:'category-snack',name:'스낵'}]:[];
  return {items,total:missing?0:base==='/stores'?2:items.length,page:Number(page??1),page_size:100};
 });
 render(<QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}><MemoryRouter><SessionProvider account={{id:'hq',role:'hq',login_id:'hq.test',display_name:'시연 본사',region_id:null,store_ids:[],version:1,is_active:true,permissions:[]}} logout={()=>{}}><Analytics/></SessionProvider></MemoryRouter></QueryClientProvider>);
 return calls;
}
it('상관표와 집계표는 현재 범위 목록의 다음 페이지까지 읽어 매장·카테고리명을 표시한다',async()=>{
 const calls=setup();const pairs=await screen.findByRole('table',{name:'상관 분석의 유효 쌍'});expect(await within(pairs).findByText('은행길점')).toBeTruthy();expect(within(pairs).getByText('스낵')).toBeTruthy();
 const report=screen.getByRole('table',{name:'범위별 집계'});expect(await within(report).findByText('은행길점')).toBeTruthy();
 expect(calls.mock.calls.some(([url])=>url.startsWith('/stores?')&&url.includes('page=2'))).toBe(true);
 expect(calls.mock.calls.every(([url])=>!url.startsWith('/operations'))).toBe(true);
});
it('이름을 얻지 못하면 대상 종류와 원본 ID를 안전하게 표시한다',async()=>{
 setup(true);const pairs=await screen.findByRole('table',{name:'상관 분석의 유효 쌍'});expect(await within(pairs).findByText('매장 이름 확인 불가 · store-bank')).toBeTruthy();expect(within(pairs).getByText('카테고리 이름 확인 불가 · category-snack')).toBeTruthy();
});
