import React from 'react';
import {afterEach,expect,it,vi} from 'vitest';
import {act,cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import {MemoryRouter} from 'react-router-dom';
import {api,type AccountMe} from '@storeloop/api-client';
import {App} from '../src/app/App';

afterEach(()=>{cleanup();vi.restoreAllMocks();});
const page=(items:unknown[])=>({items,total:items.length,page:1,page_size:20});
const account:AccountMe={id:'scope-ofc',login_id:'scope.ofc',display_name:'범위 확인 OFC',role:'ofc',region_id:'region-north',is_active:true,version:1,store_ids:[],permissions:['view_business']};
const store={id:'claim-store',name:'담당 등록 확인점',code:'CLAIM-01',region_name:'북부',store_type:'일반',is_active:true,ofc:{id:account.id,display_name:account.display_name}};

it('담당 등록 뒤 세션 범위가 먼저 갱신되어도 지연된 매장 조회가 완료되어 목록에 나타난다',async()=>{
  let claimed=false;
  let finishStores!:(value:unknown)=>void;
  const pendingStores=new Promise(resolve=>{finishStores=resolve;});
  vi.spyOn(api,'me').mockImplementation(async()=>({...account,store_ids:claimed?[store.id]:[]}));
  vi.spyOn(api,'get').mockImplementation(async(path:string)=>{
    if(path==='/stores')return claimed?pendingStores:page([]);
    if(path.startsWith('/stores/candidates'))return page(claimed?[]:[store]);
    return page([]);
  });
  vi.spyOn(api,'post').mockImplementation(async()=>{claimed=true;return store;});
  const client=new QueryClient({defaultOptions:{queries:{retry:false,staleTime:5000},mutations:{retry:false}}});
  render(<QueryClientProvider client={client}><MemoryRouter initialEntries={['/ofc-admin/stores']}><App/></MemoryRouter></QueryClientProvider>);
  await screen.findByRole('option',{name:'담당 등록 확인점 · 북부'});
  fireEvent.change(screen.getByLabelText('등록할 매장'),{target:{value:store.id}});
  fireEvent.change(screen.getByLabelText('변경 사유 (필수)'),{target:{value:'합성 담당 범위 갱신 검증'}});
  fireEvent.submit(screen.getByRole('button',{name:'담당 매장으로 등록'}).closest('form')!);
  await waitFor(()=>expect(client.getQueryData<AccountMe>(['session'])?.store_ids).toEqual([store.id]));
  await act(async()=>{finishStores(page([store]));await pendingStores;});
  await waitFor(()=>expect(screen.queryByRole('link',{name:/담당 등록 확인점/}),JSON.stringify({stores_query_present:!!client.getQueryState(['/stores']),refresh_labels:screen.queryAllByText('최신 정보를 확인하고 있습니다…').length})).not.toBeNull());
  await waitFor(()=>expect(screen.queryAllByText('최신 정보를 확인하고 있습니다…')).toHaveLength(0));
  expect(screen.queryByRole('option',{name:'담당 등록 확인점 · 북부'})).toBeNull();
  client.clear();
});

it('담당 범위가 축소되면 이전 매장 자료를 즉시 비우고 최신 범위 조회 완료를 기다린다',async()=>{
  let current={...account,store_ids:[store.id]};
  let finishScope!:(value:unknown)=>void;
  const pendingScope=new Promise(resolve=>{finishScope=resolve;});
  vi.spyOn(api,'me').mockImplementation(async()=>current);
  vi.spyOn(api,'get').mockImplementation(async(path:string)=>path==='/stores'?(current.store_ids.length?page([store]):pendingScope):page([]));
  const client=new QueryClient({defaultOptions:{queries:{retry:false,staleTime:5000}}});
  render(<QueryClientProvider client={client}><MemoryRouter initialEntries={['/ofc-admin/stores']}><App/></MemoryRouter></QueryClientProvider>);
  await screen.findByRole('link',{name:/담당 등록 확인점/});
  current={...account,version:2,store_ids:[]};
  await act(async()=>{await client.refetchQueries({queryKey:['session']});});
  await waitFor(()=>expect(client.getQueryData(['/stores'])).toBeUndefined());
  expect(screen.queryByRole('link',{name:/담당 등록 확인점/})).toBeNull();
  await act(async()=>{finishScope(page([]));await pendingScope;});
  await waitFor(()=>expect(client.getQueryState(['/stores'])?.fetchStatus).toBe('idle'));
  expect(screen.queryByRole('link',{name:/담당 등록 확인점/})).toBeNull();
  client.clear();
});

it('OFC에서 운영자로 역할이 바뀌면 영업 자료와 메뉴를 지우고 운영 메뉴만 표시한다',async()=>{
  let current:AccountMe={...account,store_ids:[store.id]};
  vi.spyOn(api,'me').mockImplementation(async()=>current);
  vi.spyOn(api,'get').mockImplementation(async(path:string)=>path==='/stores'?page([store]):page([]));
  const client=new QueryClient({defaultOptions:{queries:{retry:false,staleTime:5000}}});
  render(<QueryClientProvider client={client}><MemoryRouter initialEntries={['/ofc-admin/stores']}><App/></MemoryRouter></QueryClientProvider>);
  await screen.findByRole('link',{name:/담당 등록 확인점/});
  expect(screen.getByRole('link',{name:/관리 매장/})).toBeTruthy();
  current={...account,role:'platform_operator',region_id:null,version:2,store_ids:[],permissions:['operate']};
  await act(async()=>{await client.refetchQueries({queryKey:['session']});});
  await screen.findByRole('heading',{name:'접근 권한이 없습니다'});
  expect(screen.queryByRole('link',{name:/담당 등록 확인점/})).toBeNull();
  expect(screen.queryByRole('link',{name:/관리 매장/})).toBeNull();
  expect(screen.queryByRole('link',{name:'알림'})).toBeNull();
  expect(screen.getByRole('link',{name:/서비스 상태/})).toBeTruthy();
  expect(client.getQueryData(['/stores'])).toBeUndefined();
  client.clear();
});
