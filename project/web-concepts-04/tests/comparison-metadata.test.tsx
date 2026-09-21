// @vitest-environment jsdom
import React from 'react';
import {afterEach,expect,it,vi} from 'vitest';
import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {api} from '@storeloop/api-client';
import {Comparison} from '../src/store-owner/Owner';
import {MemoryRouter,Route,Routes} from 'react-router-dom';
afterEach(()=>{cleanup();vi.restoreAllMocks();});
const beforeDate='2026-09-20T00:00:00Z',afterDate='2026-09-21T01:30:00Z';
const rule=(key:string,version:number)=>({guideline_id:key,version_id:key+'-'+version,rule_key:key,version,text:key+' 진열 기준',level:'HQ'});
const photo=(id:string)=>({id,media_id:id,position:1,url:'/api/media/'+id,source_kind:'user_upload'});
const details={
  parent:{id:'parent',created_at:beforeDate,parent:null,context:{guidelines:[rule('removed',3),rule('facing',1)]}},
  child:{id:'child',created_at:afterDate,parent:{id:'parent',created_at:beforeDate},context:{guidelines:[rule('facing',2),rule('added',4)]}},
};
const comparison={
  parent:{submission_id:'parent',compliance_rate:25,assessable_rate:50,photos:[photo('before')]},
  current:{submission_id:'child',compliance_rate:75,assessable_rate:100,photos:[photo('after')]},
  criteria:[
    {rule_key:'facing',before:'fail',after:'pass',criterion_changed:true,change:'unavailable'},
    {rule_key:'removed',before:'pass',after:null,criterion_changed:true,change:'unavailable'},
    {rule_key:'added',before:null,after:'unknown',criterion_changed:true,change:'unavailable'},
  ],
  narrative:'적용 기준이 변경된 합성 비교입니다.',
};
function mockGet(parentFailure=false,noParent=false){
  let fail=parentFailure;
  return vi.spyOn(api,'get').mockImplementation(async<T,>(path:string)=>{
    if(path==='/submissions/child/comparison')return {...comparison,parent:noParent?null:comparison.parent} as T;
    if(path==='/submissions/child')return details.child as T;
    if(path==='/submissions/parent'){
      if(fail){fail=false;throw new Error('이전 제출 정보를 불러오지 못했습니다.');}
      return details.parent as T;
    }
    throw new Error('예상하지 않은 요청');
  });
}
function mount(){return render(<MemoryRouter initialEntries={['/store-owner/submissions/child/compare']}><Routes><Route path="/store-owner/submissions/:id/compare" element={<Comparison prefix="/store-owner"/>}/></Routes></MemoryRouter>);}
it('불변 전후 날짜와 rule_key별 버전을 구분하고 추가·제거 기준을 미적용으로 표시한다',async()=>{
  const get=mockGet();const {container}=mount();
  await screen.findByText('이전 기준 v1 → 현재 기준 v2');
  expect(screen.getByText('이전 기준 v3 → 현재 기준 미적용')).toBeTruthy();
  expect(screen.getByText('이전 기준 미적용 → 현재 기준 v4')).toBeTruthy();
  const times=Array.from(container.querySelectorAll('time'));
  expect(times.map(item=>item.getAttribute('datetime'))).toEqual([beforeDate,afterDate]);
  expect(times.every(item=>item.textContent?.includes('2026'))).toBe(true);
  expect(screen.getByText('적용 기준이 달라 단순 점수 비교에 주의가 필요합니다.')).toBeTruthy();
  expect(screen.getByText(/25%/)).toBeTruthy();expect(screen.getByText(/75%/)).toBeTruthy();
  expect(screen.getAllByRole('img').map(item=>item.getAttribute('src'))).toEqual(['/api/media/before','/api/media/after']);
  expect(container.textContent).not.toContain('기준 v0');
  expect(new Set(get.mock.calls.map(([path])=>path))).toEqual(new Set(['/submissions/child/comparison','/submissions/child','/submissions/parent']));
});
it('부모 상세 조회 실패를 표시하고 재시도 후에만 과거 버전을 표시한다',async()=>{
  mockGet(true);mount();
  await screen.findByText('이전 제출 정보를 불러오지 못했습니다.');
  expect(screen.queryByText('이전 기준 v1 → 현재 기준 v2')).toBeNull();
  fireEvent.click(screen.getByRole('button',{name:'상태를 다시 확인'}));
  await screen.findByText('이전 기준 v1 → 현재 기준 v2');
});
it('부모가 없는 기록은 빈 상태를 유지하고 임의 부모 상세를 조회하지 않는다',async()=>{
  const get=mockGet(false,true);mount();
  await screen.findByText('이전 제출이 없는 기록입니다.');
  await waitFor(()=>expect(get.mock.calls.some(([path])=>path==='/submissions/parent')).toBe(false));
  expect(screen.queryByText(/이전 기준 v/)).toBeNull();
});
