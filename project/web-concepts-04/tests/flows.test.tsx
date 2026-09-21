// @vitest-environment jsdom
import React from 'react';
import {afterEach,beforeEach,describe,it,expect,vi} from 'vitest';
import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {MemoryRouter,Route,Routes} from 'react-router-dom';
import {api,ApiError,Session,useData} from '../src/shared/data';
import {Submit} from '../src/store-owner/Owner';
import {Filters,MutationForm,Field,Reason,DataState} from '../src/shared/ui';
vi.mock('@storeloop/api-client',async()=>{const original=await vi.importActual<any>('@storeloop/api-client');return {...original,api:{...original.api,get:vi.fn(),upload:vi.fn()}};});
const account={id:'owner1',login_id:'owner.test',display_name:'시연 점주',role:'store_owner' as const,region_id:null,is_active:true,version:1,store_ids:['store1'],permissions:['submit']};
function mount(ui:React.ReactNode,path='/store-owner/submit'){return render(<MemoryRouter initialEntries={[path]}><Session.Provider value={{account,refresh:async()=>{}}}>{ui}</Session.Provider></MemoryRouter>);}
beforeEach(()=>{vi.mocked(api.get).mockImplementation(async(path:string)=>({items:path.startsWith('/stores')?[{id:'store1',name:'봄빛역점',can_submit:true}]:[{id:'category1',name:'음료'}],total:1,page:1,page_size:20}) as any);URL.createObjectURL=vi.fn(()=>'/preview');URL.revokeObjectURL=vi.fn();});
afterEach(()=>{cleanup();vi.clearAllMocks();});
describe('실제 화면 흐름의 경계',()=>{
 it('제출 네 단계를 진행하고 네트워크 재시도에는 같은 키를 보존한다',async()=>{
  vi.mocked(api.upload).mockRejectedValueOnce(new ApiError(0,'NETWORK_ERROR','연결을 확인한 뒤 다시 시도해 주세요.')).mockResolvedValueOnce({submission_id:'accepted1'});
  mount(<Routes><Route path="/store-owner/submit" element={<Submit/>}/><Route path="/store-owner/submissions/:id" element={<h1>접수한 기록</h1>}/></Routes>);
  await screen.findByRole('option',{name:'봄빛역점'});
  fireEvent.change(screen.getByLabelText('매장'),{target:{value:'store1'}});fireEvent.change(screen.getByLabelText('매대 카테고리'),{target:{value:'category1'}});
  fireEvent.click(screen.getByRole('button',{name:'다음 단계 →'}));
  const first=new File(['first'],'first.png',{type:'image/png'}),second=new File(['second'],'second.png',{type:'image/png'});
  fireEvent.change(screen.getByLabelText(/사진 선택/),{target:{files:[first,second]}});
  fireEvent.click(screen.getByLabelText('사진 2 앞으로'));
  fireEvent.click(screen.getByRole('button',{name:'다음 단계 →'}));
  fireEvent.change(screen.getByLabelText(/질문 또는 현장 설명/),{target:{value:'앞줄을 확인해 주세요.'}});
  fireEvent.click(screen.getByRole('button',{name:'이전'}));
  expect(screen.getAllByAltText(/선택한 사진/)).toHaveLength(2);
  fireEvent.click(screen.getByRole('button',{name:'다음 단계 →'}));fireEvent.click(screen.getByRole('button',{name:'다음 단계 →'}));
  fireEvent.click(screen.getByRole('button',{name:'사진 제출하기'}));await screen.findByText('연결을 확인한 뒤 다시 시도해 주세요.');
  fireEvent.click(screen.getByRole('button',{name:'사진 제출하기'}));await screen.findByText('접수한 기록');
  const calls=vi.mocked(api.upload).mock.calls;
  expect(calls).toHaveLength(2);expect(calls[0][3]).toBe(calls[1][3]);expect(calls[0][1]).toMatchObject({store_id:'store1',category_id:'category1',question:'앞줄을 확인해 주세요.',parent_submission_id:null});expect(calls[0][2].map(f=>f.file.name)).toEqual(['second.png','first.png']);
 });
 it('현재 단계 입력이 빠지면 다음으로 이동하지 않는다',async()=>{mount(<Submit/>);await screen.findByRole('option',{name:'봄빛역점'});fireEvent.click(screen.getByRole('button',{name:'다음 단계 →'}));expect(screen.getByRole('alert').textContent).toContain('매장과 카테고리');expect(screen.getByRole('heading',{level:1}).textContent).toContain('어느 매장');expect(api.upload).not.toHaveBeenCalled();});
 it('운영 변경은 확인 단계를 거치고 충돌 때 입력을 유지한다',async()=>{const reload=vi.fn();const save=vi.fn().mockRejectedValue(new ApiError(409,'VERSION_CONFLICT','다른 변경이 먼저 반영됐습니다.'));mount(<MutationForm onSave={save} onConflict={reload} confirm><Field label="이름"><input name="name" defaultValue="새 이름"/></Field><Reason/></MutationForm>);fireEvent.change(screen.getByLabelText('변경 사유'),{target:{value:'담당 변경 확인'}});fireEvent.click(screen.getByRole('button',{name:'내용 확인'}));expect(save).not.toHaveBeenCalled();expect(screen.getByText('변경 내용을 확인해 주세요')).toBeTruthy();fireEvent.click(screen.getByRole('button',{name:'변경 저장'}));await screen.findByText('다른 변경이 먼저 반영됐습니다.');fireEvent.click(screen.getByRole('button',{name:'상태를 다시 확인'}));expect(reload).toHaveBeenCalledOnce();expect((screen.getByLabelText('이름') as HTMLInputElement).value).toBe('새 이름');expect((screen.getByLabelText('변경 사유') as HTMLInputElement).value).toBe('담당 변경 확인');});
 it('권한 오류 후 이전 데이터를 표시하지 않는다',async()=>{vi.mocked(api.get).mockResolvedValueOnce({secret:'이전 사진 설명'}).mockRejectedValue(new ApiError(403,'FORBIDDEN','접근할 수 없습니다.'));function Probe(){const s=useData('/submissions/one');return <><DataState state={s}><p>{s.data?.secret}</p></DataState><button onClick={s.reload}>갱신</button></>;}mount(<Probe/>);await screen.findByText('이전 사진 설명');fireEvent.click(screen.getByRole('button',{name:'갱신'}));await screen.findByText('접근할 수 없습니다.');expect(screen.queryByText('이전 사진 설명')).toBeNull();});
});
describe('MEDIA-CLARIFY-1 적용 Reference',()=>{
 const detail={id:'s1',store_id:'store1',store_name:'시연 매장',category_name:'음료',created_at:'2026-09-21T00:00:00Z',submitted_by_id:'owner1',question:'',job:{status:'failed',error_message:'시연 실패',attempt_count:1},photos:[{id:'submission',url:'/api/media/submission',position:1,source_kind:'user_upload'}],review:null,context:{guidelines:[],references:[{reference_id:'a',photo_id:'old-a',caption:'첫 예시',position:1},{reference_id:'b',photo_id:'old-b',caption:'둘째 예시',position:2}]},parent:null,children:[],issues:[]};
 it('metadata 순서와 무관하게 snapshot ID에 연결하고 실제 출처만 표시한다',async()=>{const {SubmissionDetail}=await import('../src/store-owner/Owner');vi.mocked(api.get).mockResolvedValue({...detail,reference_photos:[{reference_id:'b',photo:{url:'/api/media/protected-b',source_kind:'ai_generated_demo'}},{reference_id:'unrelated',photo:{url:'/api/media/unrelated',source_kind:'ai_generated_demo'}},{reference_id:'a',photo:{url:'/api/media/protected-a',source_kind:'user_upload'}}]});mount(<Routes><Route path="/store-owner/submissions/:id" element={<SubmissionDetail prefix="/store-owner"/>}/></Routes>,'/store-owner/submissions/s1');await screen.findByAltText('첫 예시');expect(screen.getByAltText('첫 예시').getAttribute('src')).toBe('/api/media/protected-a');expect(screen.getByAltText('둘째 예시').getAttribute('src')).toBe('/api/media/protected-b');expect(screen.getAllByText('AI 생성 시연 이미지')).toHaveLength(1);expect(vi.mocked(api.get).mock.calls.every(([path])=>path==='/submissions/s1')).toBe(true);});
 it('metadata가 없으면 photo_id만 사용하고 Reference 출처를 추정하지 않는다',async()=>{const {SubmissionDetail}=await import('../src/store-owner/Owner');vi.mocked(api.get).mockResolvedValue(detail);mount(<Routes><Route path="/store-owner/submissions/:id" element={<SubmissionDetail prefix="/store-owner"/>}/></Routes>,'/store-owner/submissions/s1');await screen.findByAltText('첫 예시');expect(screen.getByAltText('첫 예시').getAttribute('src')).toBe('/api/media/old-a');expect(screen.queryByText('AI 생성 시연 이미지')).toBeNull();expect(screen.getAllByText('제출 사진')).toHaveLength(1);});
});
