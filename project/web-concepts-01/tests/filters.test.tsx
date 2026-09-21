import React from 'react';
import {afterEach,it,expect,vi} from 'vitest';
import {act,cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {MemoryRouter,useLocation,useNavigate} from 'react-router-dom';
import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import {api} from '@storeloop/api-client';
import {SessionProvider} from '../src/app/session';
import {ScopeFilters} from '../src/shared/business';
import {useFilters} from '../src/shared/data';

afterEach(()=>{cleanup();vi.restoreAllMocks();});
function FilterPage(){const filters=useFilters(),location=useLocation(),navigate=useNavigate();return <><ScopeFilters filter={filters}/><output aria-label="현재 조회 주소">{location.search}</output><button onClick={()=>filters.updateMany({status:'open',unresolved:''})}>처리 상태 선택</button><button onClick={()=>navigate(-1)}>뒤로</button></>;}
function setup(initial='/ofc-admin/submissions?status=failed&page=4'){
 vi.spyOn(api,'get').mockImplementation(async(path:string)=>({items:path.startsWith('/stores')?[{id:'bank',name:'은행길점'}]:path.startsWith('/categories')?[{id:'snack',name:'스낵'}]:[],total:1,page:1,page_size:20}) as any);
 render(<QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}><MemoryRouter initialEntries={[initial]}><SessionProvider account={{id:'ofc',role:'ofc',login_id:'ofc.test',display_name:'시연 OFC',region_id:'north',store_ids:['bank'],version:1,is_active:true,permissions:[]}} logout={()=>{}}><FilterPage/></SessionProvider></MemoryRouter></QueryClientProvider>);
}
function current(){return Object.fromEntries(new URLSearchParams(screen.getByLabelText('현재 조회 주소').textContent??''));}

it('같은 렌더 사이 빠른 매장·카테고리·기간 변경은 모두 합쳐 URL과 입력에 남는다',async()=>{
 setup();await screen.findByRole('option',{name:'은행길점'});
 act(()=>{
  fireEvent.change(screen.getByLabelText('매장'),{target:{value:'bank'}});
  fireEvent.change(screen.getByLabelText('카테고리'),{target:{value:'snack'}});
  fireEvent.change(screen.getByLabelText('시작 날짜 (UTC)'),{target:{value:'2026-09-01'}});
  fireEvent.change(screen.getByLabelText('종료 날짜 (UTC)'),{target:{value:'2026-09-21'}});
 });
 await waitFor(()=>expect(current()).toEqual({status:'failed',page:'1',store_id:'bank',category_id:'snack',date_from:'2026-09-01',date_to:'2026-09-21'}));
 expect((screen.getByLabelText('매장') as HTMLSelectElement).value).toBe('bank');
 expect((screen.getByLabelText('카테고리') as HTMLSelectElement).value).toBe('snack');
});

it('하나의 조건만 해제하고 상태 일괄 변경해도 다른 범위·기간은 유지한다',async()=>{
 setup('/ofc-admin/issues?store_id=bank&category_id=snack&date_from=2026-09-01&unresolved=true&page=4');await screen.findByRole('option',{name:'은행길점'});
 act(()=>{
  fireEvent.change(screen.getByLabelText('카테고리'),{target:{value:''}});
  fireEvent.click(screen.getByRole('button',{name:'처리 상태 선택'}));
 });
 await waitFor(()=>expect(current()).toEqual({store_id:'bank',date_from:'2026-09-01',page:'1',status:'open'}));
});

it('뒤로 돌아간 URL과 초기화가 다음 변경의 기준이 되어 오래된 조건을 복원하지 않는다',async()=>{
 setup('/ofc-admin/submissions?date_from=2026-09-01');await screen.findByRole('option',{name:'은행길점'});
 fireEvent.change(screen.getByLabelText('매장'),{target:{value:'bank'}});await waitFor(()=>expect(current().store_id).toBe('bank'));
 fireEvent.click(screen.getByRole('button',{name:'뒤로'}));await waitFor(()=>expect(current()).toEqual({date_from:'2026-09-01'}));
 fireEvent.change(screen.getByLabelText('카테고리'),{target:{value:'snack'}});await waitFor(()=>expect(current()).toEqual({date_from:'2026-09-01',category_id:'snack',page:'1'}));
 act(()=>{fireEvent.click(screen.getByRole('button',{name:'필터 초기화'}));fireEvent.change(screen.getByLabelText('매장'),{target:{value:'bank'}});});
 await waitFor(()=>expect(current()).toEqual({store_id:'bank',page:'1'}));
});
