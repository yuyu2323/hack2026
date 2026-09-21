// @vitest-environment jsdom
import React from 'react';
import {afterEach,beforeEach,describe,it,expect,vi} from 'vitest';
import {cleanup,fireEvent,render,screen,within,waitFor} from '@testing-library/react';
import {MemoryRouter} from 'react-router-dom';
import {api,ApiError,Session} from '../src/shared/data';
import {References} from '../src/ofc-admin/Standards';
vi.mock('@storeloop/api-client',async()=>{const actual=await vi.importActual<any>('@storeloop/api-client');return {...actual,api:{...actual.api,get:vi.fn(),upload:vi.fn()}};});
const account={id:'hq1',login_id:'hq.fixture',display_name:'합성 본사',role:'hq' as const,region_id:null,is_active:true,version:1,store_ids:[],permissions:['manage_guidelines']};
const original={id:'reference-old',lineage_id:'lineage-one',version:1,state_version:1,category_id:'category1',store_id:null,caption:'이전 Reference 설명',is_active:true,created_at:'2026-09-21T00:00:00Z',photo:{id:'photo-old',url:'/api/media/photo-old',source_kind:'user_upload'}};
const latest={...original,id:'reference-new',version:2,state_version:3,caption:'다른 사람이 저장한 설명',photo:{...original.photo,id:'photo-new',url:'/api/media/photo-new'}};
const page=(items:any[])=>({items,total:items.length,page:1,page_size:100});
const BrowserFormData=globalThis.FormData;
beforeEach(()=>{
 // jsdom의 fireEvent 파일목록을 실제 브라우저 FormData 직렬화와 동일하게 연결한다.
 vi.stubGlobal('FormData',class extends BrowserFormData{constructor(form?:HTMLFormElement,submitter?:HTMLElement|null){super(form,submitter);form?.querySelectorAll<HTMLInputElement>('input[type=file]').forEach(input=>{if(input.name&&input.files?.length){this.delete(input.name);Array.from(input.files).forEach(file=>this.append(input.name,file));}});}});
 URL.createObjectURL=vi.fn(()=>'/preview-selected');URL.revokeObjectURL=vi.fn();});
afterEach(()=>{cleanup();vi.clearAllMocks();vi.unstubAllGlobals();});
describe('IB-C03 실제 Reference 편집 충돌',()=>{
 it.each(['','?include_inactive=true'])('목록 %s: 새 revision 확인 후 사진·설명·사유 보존과 명시 재저장',async(search)=>{
  let referenceReads=0;
  vi.mocked(api.get).mockImplementation(async(path:string)=>{
   if(path.startsWith('/references')){referenceReads++;const historical={...original,id:'reference-history',version:0,is_active:false,caption:'과거 사진 설명'};return page(referenceReads===1?(search?[original,historical]:[original]):[latest,{...original,is_active:false},historical]) as any;}
   return page([]) as any;
  });
  vi.mocked(api.upload).mockRejectedValueOnce(new ApiError(409,'VERSION_CONFLICT','다른 변경이 먼저 반영됐습니다.')).mockResolvedValueOnce({...latest,id:'reference-saved',version:3});
  render(<MemoryRouter initialEntries={['/ofc-admin/references'+search]}><Session.Provider value={{account,refresh:async()=>{}}}><References/></Session.Provider></MemoryRouter>);
  const card=(await screen.findByAltText('이전 Reference 설명')).closest('section')!;
  const disclosure=within(card).getByText('사진·설명 새 버전');
  fireEvent.click(disclosure);
  const editor=disclosure.closest('details')!;
  const caption=within(editor).getByLabelText('사진 설명') as HTMLTextAreaElement;
  const reason=within(editor).getByLabelText('변경 사유') as HTMLTextAreaElement;
  const input=within(editor).getByLabelText(/교체할 사진/)  as HTMLInputElement;
  const file=new File(['synthetic image'],'replacement.png',{type:'image/png'});
  fireEvent.change(caption,{target:{value:'내가 작성 중인 설명'}});
  fireEvent.change(reason,{target:{value:'현장 Reference 사진 교체'}});
  fireEvent.change(input,{target:{files:[file]}});
  expect(await within(editor).findByAltText('선택한 Reference 사진 미리보기')).toBeTruthy();
  fireEvent.click(within(editor).getByRole('button',{name:'새 Reference 저장'}));
  await within(editor).findByText('다른 변경이 먼저 반영됐습니다.');
  fireEvent.click(within(editor).getByRole('button',{name:'상태를 다시 확인'}));
  await waitFor(()=>expect(referenceReads).toBeGreaterThan(1));
  await within(editor).findByText(/최신 버전 2의 정보를 확인했습니다/);
  const freshEditor=within(card).getByText('사진·설명 새 버전').closest('details')!;
  expect((within(freshEditor).getByLabelText('사진 설명') as HTMLTextAreaElement).value).toBe('내가 작성 중인 설명');
  expect((within(freshEditor).getByLabelText('변경 사유') as HTMLTextAreaElement).value).toBe('현장 Reference 사진 교체');
  expect((within(freshEditor).getByLabelText(/교체할 사진/)  as HTMLInputElement).files?.[0]).toBe(file);
  expect(within(freshEditor).getByAltText('선택한 Reference 사진 미리보기')).toBeTruthy();
  expect(api.upload).toHaveBeenCalledTimes(1);
  fireEvent.click(within(freshEditor).getByRole('button',{name:'새 Reference 저장'}));
  await waitFor(()=>expect(api.upload).toHaveBeenCalledTimes(2));
  expect(vi.mocked(api.upload).mock.calls[1][0]).toBe('/references/reference-new');
  expect(vi.mocked(api.upload).mock.calls[1][1]).toEqual({state_version:3,caption:'내가 작성 중인 설명',reason:'현장 Reference 사진 교체'});
  expect(vi.mocked(api.upload).mock.calls[1][2][0]?.file).toBe(file);
 });
});
