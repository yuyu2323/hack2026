import React from 'react';
import {afterEach,beforeEach,it,expect,vi} from 'vitest';
import {cleanup,render,screen,fireEvent,waitFor,act} from '@testing-library/react';
import {QueryClientProvider} from '@tanstack/react-query';
import {MemoryRouter} from 'react-router-dom';
import {api,ApiError,type AccountMe} from '../../../packages/api-client/src/index';
import {App} from '../../../web-concepts-01/src/app/App';
import {createAppQueryClient} from '../../../web-concepts-01/src/app/query-client';

const account:AccountMe={id:'independent-hq',login_id:'synthetic.hq',display_name:'합성 검수',role:'hq',region_id:null,is_active:true,version:1,store_ids:[],permissions:[]};
const old={id:'reference-a1',lineage_id:'lineage-a',version:1,state_version:1,category_id:'category-one',store_id:null,caption:'처음 A',is_active:true,photo:{id:'media-a',url:'/api/media/media-a'}};
const other={...old,id:'reference-b1',lineage_id:'lineage-b',caption:'다른 B'};
const page=(items:unknown[])=>({items,total:items.length,page:1,page_size:100});
const clients:ReturnType<typeof createAppQueryClient>[]=[];
function mount(recovery:()=>Promise<unknown>) {
  vi.spyOn(api,'me').mockResolvedValue(account);
  vi.spyOn(api,'get').mockImplementation(async<T,>(path:string)=>{
    if(path.startsWith('/references')) {
      if(new URL(path,'http://synthetic.invalid').searchParams.get('include_inactive')==='true') return await recovery() as T;
      return page([old,other]) as T;
    }
    if(path.startsWith('/categories'))return page([{id:'category-one',name:'음료'}]) as T;
    if(path.startsWith('/stores')||path.startsWith('/regions')||path.startsWith('/announcements')||path.startsWith('/notifications')) return page([]) as T;
    throw new Error('허용하지 않은 합성 조회');
  });
  const upload=vi.spyOn(api,'upload').mockRejectedValueOnce(new ApiError(409,'VERSION_CONFLICT','합성 충돌')).mockImplementationOnce(()=>new Promise(()=>{}));
  const client=createAppQueryClient();clients.push(client);
  render(<QueryClientProvider client={client}><MemoryRouter initialEntries={['/ofc-admin/references']}><App/></MemoryRouter></QueryClientProvider>);
  return {client,upload};
}
async function startRecovery(){
  fireEvent.click((await screen.findAllByRole('button',{name:'사진 · 설명 수정'}))[0]);
  fireEvent.change(screen.getByLabelText('사진 설명'),{target:{value:'A의 작성 초안'}});
  fireEvent.change(screen.getAllByLabelText('변경 사유 (필수)').at(-1)!,{target:{value:'A 변경 사유'}});
  fireEvent.submit(screen.getByRole('button',{name:'새 버전 저장'}).closest('form')!);
  fireEvent.click(await screen.findByRole('button',{name:'최신 Reference 확인 (입력 유지)'}));
}
beforeEach(()=>{HTMLElement.prototype.scrollIntoView=vi.fn();});
afterEach(()=>{cleanup();clients.splice(0).forEach(c=>c.clear());vi.restoreAllMocks();});

it('이전 A의 늦은 응답은 B 편집 대상과 B의 다음 저장 대상을 바꾸지 않는다',async()=>{
  let release!:(value:unknown)=>void;
  const pending=new Promise(value=>{release=value;});
  const recovery=vi.fn(()=>pending);
  const {upload}=mount(recovery);
  await startRecovery();await waitFor(()=>expect(recovery).toHaveBeenCalledTimes(1));
  fireEvent.click(screen.getAllByRole('button',{name:'사진 · 설명 수정'})[1]);
  fireEvent.change(screen.getByLabelText('사진 설명'),{target:{value:'B에만 저장할 설명'}});
  fireEvent.change(screen.getAllByLabelText('변경 사유 (필수)').at(-1)!,{target:{value:'B 변경 사유'}});
  await act(async()=>release(page([{...old,id:'reference-a2',version:2,state_version:3}])));
  fireEvent.submit(screen.getByRole('button',{name:'새 버전 저장'}).closest('form')!);
  await waitFor(()=>expect(upload).toHaveBeenCalledTimes(2));
  expect(upload.mock.calls[1][0]).toBe('/references/reference-b1');
  expect(upload.mock.calls[1][1]).toEqual({state_version:1,caption:'B에만 저장할 설명',reason:'B 변경 사유'});
});

it('복구 조회의403도 production App 권한철회 경로로 업무 캐시를 즉시 폐기한다',async()=>{
  const {client}=mount(async()=>{throw new ApiError(403,'FORBIDDEN','합성 권한 철회');});
  await startRecovery();
  await screen.findByText('현재 권한으로 접근할 수 없습니다.');
  expect(client.getQueryData(['/references'])).toBeUndefined();
});
