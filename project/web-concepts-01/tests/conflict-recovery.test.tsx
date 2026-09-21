import React from 'react';
import {afterEach,it,expect,vi} from 'vitest';
import {cleanup,render,screen,fireEvent,waitFor} from '@testing-library/react';
import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import {MemoryRouter,Routes,Route} from 'react-router-dom';
import {api,ApiError,type AccountMe} from '@storeloop/api-client';
import {SessionProvider} from '../src/app/session';
import {GuidelineDetail,References} from '../src/ofc-admin/Standards';

afterEach(()=>{cleanup();vi.restoreAllMocks();vi.unstubAllGlobals();});
const account:AccountMe={id:'review-hq',login_id:'review.hq',display_name:'검수 본사',role:'hq',region_id:null,is_active:true,version:1,store_ids:['store'],permissions:[]};
const page=(items:unknown[])=>({items,total:items.length,page:1,page_size:20});
function mount(view:React.ReactNode,path:string){const client=new QueryClient({defaultOptions:{queries:{retry:false,staleTime:5000},mutations:{retry:false}}});render(<QueryClientProvider client={client}><SessionProvider account={account} logout={()=>{}}><MemoryRouter initialEntries={[path]}><Routes><Route path="/ofc-admin/guidelines/:id" element={view}/><Route path="/ofc-admin/references" element={view}/></Routes></MemoryRouter></SessionProvider></QueryClientProvider>);return client;}

it('기준409 최신 조회 뒤 초안과 사유를 보존하고 최신 version으로 명시 재저장한다',async()=>{
 let version=1;
 const guideline=()=>({id:'g1',rule_key:'facing',title:'검증 기준',level:'HQ',version,current_version:version,current:{text:version===1?'기존 본문':'다른 사람이 저장한 본문'},is_active:false});
 vi.spyOn(api,'get').mockImplementation(async(path:string)=>path==='/guidelines/g1'?guideline():page([]));
 const post=vi.spyOn(api,'post').mockImplementation(async()=>{if(version===1){version=2;throw new ApiError(409,'VERSION_CONFLICT','버전 충돌');}return guideline();});
 const client=mount(<GuidelineDetail/>,'/ofc-admin/guidelines/g1');
 await screen.findByLabelText('기준 내용');
 fireEvent.change(screen.getByLabelText('기준 내용'),{target:{value:'사용자가 유지할 초안'}});
 fireEvent.change(screen.getAllByLabelText('변경 사유 (필수)')[0],{target:{value:'유지할 변경 사유'}});
 fireEvent.submit(screen.getByRole('button',{name:'새 버전 저장'}).closest('form')!);
 await screen.findByText(/현재 버전 2/);
 expect((screen.getByLabelText('기준 내용') as HTMLTextAreaElement).value).toBe('사용자가 유지할 초안');
 expect((screen.getAllByLabelText('변경 사유 (필수)')[0] as HTMLInputElement).value).toBe('유지할 변경 사유');
 expect(post).toHaveBeenCalledTimes(1);
 fireEvent.submit(screen.getByRole('button',{name:'새 버전 저장'}).closest('form')!);
 await waitFor(()=>expect(post).toHaveBeenCalledTimes(2));
 expect(post.mock.calls[1][1]).toMatchObject({version:2,text:'사용자가 유지할 초안',reason:'유지할 변경 사유'});
 client.clear();
});

it('Reference409 후 같은 lineage의 최신 대상으로 전환하며 선택 파일과 설명·사유를 유지한다',async()=>{
 let conflicted=false;
 const old={id:'r1',lineage_id:'lineage1',version:1,state_version:1,category_id:'cat1',store_id:null,caption:'원래 설명',is_active:true,photo:{id:'p1',url:'/api/media/p1'}};
 const latest={...old,id:'r2',version:2,state_version:3,is_active:false};
 vi.spyOn(api,'get').mockImplementation(async(path:string)=>path.startsWith('/references')?page(conflicted?[latest,{...old,is_active:false}]:[old]):path.startsWith('/categories')?page([{id:'cat1',name:'음료'}]):page([]));
 const upload=vi.spyOn(api,'upload').mockImplementation(async(path:string,metadata:any)=>{if(!conflicted){conflicted=true;throw new ApiError(409,'VERSION_CONFLICT','Reference 충돌');}if(path!=='/references/r2'||metadata.state_version!==3)throw new ApiError(409,'VERSION_CONFLICT','이전 revision');return {...latest,id:'r3',version:3};});
 HTMLElement.prototype.scrollIntoView=vi.fn();
 // jsdom의 file input FormData 변환은 fireEvent로 지정한 FileList를 읽지 않아 브라우저 동작을 보완한다.
 const NativeFormData=globalThis.FormData;
 vi.stubGlobal('FormData',class extends NativeFormData{constructor(form?:HTMLFormElement){super(form);form?.querySelectorAll<HTMLInputElement>('input[type=file]').forEach(input=>{this.delete(input.name);Array.from(input.files??[]).forEach(file=>this.append(input.name,file));});}});
 const client=mount(<References/>,'/ofc-admin/references');
 fireEvent.click(await screen.findByRole('button',{name:'사진 · 설명 수정'}));
 fireEvent.change(screen.getByLabelText('사진 설명'),{target:{value:'유지할 사진 설명'}});
 fireEvent.change(screen.getAllByLabelText('변경 사유 (필수)').at(-1)!,{target:{value:'유지할 교체 사유'}});
 const file=new File(['synthetic'],'replacement.png',{type:'image/png'});
 fireEvent.change(screen.getByLabelText(/새 사진 \(선택\)/),{target:{files:[file]}});
 fireEvent.submit(screen.getByRole('button',{name:'새 버전 저장'}).closest('form')!);
 await screen.findByText('다른 변경이 먼저 적용되었습니다. 최신 정보를 확인해 주세요.');
 const refresh=screen.queryByRole('button',{name:'최신 Reference 확인 (입력 유지)'});
 if(refresh){fireEvent.click(refresh);await screen.findByText('현재 Reference 버전 2');}
 expect((screen.getByLabelText('사진 설명') as HTMLTextAreaElement).value).toBe('유지할 사진 설명');
 expect((screen.getAllByLabelText('변경 사유 (필수)').at(-1)! as HTMLInputElement).value).toBe('유지할 교체 사유');
 expect((screen.getByLabelText(/새 사진 \(선택\)/) as HTMLInputElement).files?.[0]).toBe(file);
 expect(upload).toHaveBeenCalledTimes(1);
 fireEvent.submit(screen.getByRole('button',{name:'새 버전 저장'}).closest('form')!);
 await waitFor(()=>expect(upload).toHaveBeenCalledTimes(2));
 expect(upload.mock.calls[1].slice(0,3)).toEqual(['/references/r2',{state_version:3,caption:'유지할 사진 설명',reason:'유지할 교체 사유'},[{field:'photo',file}]]);
 client.clear();
});
