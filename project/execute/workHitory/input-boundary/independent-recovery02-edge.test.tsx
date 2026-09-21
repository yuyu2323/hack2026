import React from 'react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen, waitFor, within, act } from '@testing-library/react';
import { api, ApiError, type AccountMe } from '../../../packages/api-client/src/index';
import { accessFailure } from '../../../web-concepts-02/src/shared/core';
import { References } from '../../../web-concepts-02/src/ofc-admin/Standards';

const account: AccountMe = {id:'synthetic-hq',login_id:'synthetic-hq',display_name:'합성 본사',role:'hq',region_id:null,is_active:true,version:1,store_ids:[],permissions:[]};
const page = (items: unknown[], number=1, total=items.length) => ({items,page:number,page_size:100,total});
const old = {id:'reference-one',lineage_id:'lineage-one',version:1,state_version:1,caption:'첫 Reference',category_id:'category-one',store_id:null,is_active:true,created_at:'2026-09-21T00:00:00Z',photo:{id:'media-one',position:1,url:'/api/media/media-one',source_kind:'user_upload'}};
const other = {...old,id:'reference-other',lineage_id:'lineage-other',caption:'둘째 Reference'};
function setup(resolve:(path:string)=>unknown|Promise<unknown>) {
  history.replaceState({},'', '/ofc-admin/references');
  return vi.spyOn(api,'get').mockImplementation(async <T,>(path:string) => {
    if(path.startsWith('/references')) return await resolve(path) as T;
    if(path.startsWith('/stores') || path.startsWith('/regions')) return page([]) as T;
    if(path.startsWith('/categories')) return page([{id:'category-one',name:'음료'}]) as T;
    throw new Error('허용하지 않은 합성 요청 경로');
  });
}
async function openDraft() {
  const buttons=await screen.findAllByRole('button',{name:'사진·설명 교체'});
  fireEvent.click(buttons[0]);
  const form=screen.getByRole('heading',{name:'Reference 새 버전으로 교체'}).closest('form')!;
  fireEvent.change(within(form).getByRole('textbox',{name:/이 사진에서 참고할 점/}),{target:{value:'보존할 작성 설명'}});
  fireEvent.change(within(form).getByRole('textbox',{name:/변경 사유/}),{target:{value:'보존할 사유'}});
  const file=new File(['synthetic'], 'preserved.png',{type:'image/png'});
  fireEvent.change(within(form).getByLabelText(/매대 사진 선택/),{target:{files:[file]}});
  fireEvent.click(within(form).getByRole('button',{name:'새 버전 저장'}));
  fireEvent.click(await within(form).findByRole('button',{name:'최신 정보 다시 읽기'}));
  return {form,file};
}
beforeEach(()=>{
  URL.createObjectURL=vi.fn(()=> 'blob:independent-review');
  URL.revokeObjectURL=vi.fn();
});
afterEach(()=>{cleanup();vi.restoreAllMocks();});

it('CSRF만 권한철회 이벤트에서 제외하고 일반403·401·404는 기존 차단 경로를 유지한다',()=>{
  const listener=vi.fn();window.addEventListener('storeloop-access',listener);
  try {
    accessFailure(new ApiError(403,'CSRF_INVALID','합성 CSRF 오류'));
    expect(listener).not.toHaveBeenCalled();
    for(const [status,code] of [[403,'FORBIDDEN'],[403,'ORIGIN_DENIED'],[401,'AUTH_REQUIRED'],[404,'NOT_FOUND']] as const) {
      const error=new ApiError(status,code,'합성 권한 오류');accessFailure(error);
      expect(listener.mock.calls.at(-1)![0].detail).toBe(error);
    }
    expect(listener).toHaveBeenCalledTimes(4);
  } finally {window.removeEventListener('storeloop-access',listener);}
});

it('페이지 밖의 비활성 최신 lineage를 골라 초안·파일을 보존하고 명시 재저장만 허용한다',async()=>{
  const latest={...old,id:'reference-new',version:2,state_version:4,is_active:false,caption:'현재 서버 설명'};
  const recoveryPaths:string[]=[];
  setup((path)=>{
    const q=new URL(path,'http://synthetic.invalid').searchParams;
    if(q.get('include_inactive')==='true') {
      recoveryPaths.push(path);
      return q.get('page')==='1'
        ? page([{...other,version:99}, {...old,state_version:2}],1,101)
        : page([{...latest,state_version:3},latest],2,101);
    }
    return page([old,other]);
  });
  const upload=vi.spyOn(api,'upload').mockRejectedValueOnce(new ApiError(409,'VERSION_CONFLICT','합성 충돌')).mockImplementationOnce(()=>new Promise(()=>{}));
  render(<References account={account}/>);
  const {form,file}=await openDraft();
  await within(form).findByText('최신 Reference v2를 확인했습니다.');
  expect(upload).toHaveBeenCalledTimes(1);
  expect(recoveryPaths).toHaveLength(2);
  expect(recoveryPaths.every(path=>new URL(path,'http://synthetic.invalid').searchParams.get('category_id')==='category-one')).toBe(true);
  expect((within(form).getByRole('textbox',{name:/이 사진에서 참고할 점/}) as HTMLInputElement).value).toBe('보존할 작성 설명');
  fireEvent.click(within(form).getByRole('button',{name:'새 버전 저장'}));
  await waitFor(()=>expect(upload).toHaveBeenCalledTimes(2));
  expect(upload.mock.calls[1][0]).toBe('/references/reference-new');
  expect(upload.mock.calls[1][1]).toEqual({state_version:4,caption:'보존할 작성 설명',reason:'보존할 사유'});
  expect(upload.mock.calls[1][2][0].file).toBe(file);
});

it('다른 Reference 편집 후 늦게 온 복구 응답은 새 대상·초안을 덮지 않는다',async()=>{
  let resolve!:(value:unknown)=>void;
  const pending=new Promise(value=>{resolve=value;});
  let recoveryCalls=0;
  setup(path=>{
    if(new URL(path,'http://synthetic.invalid').searchParams.get('include_inactive')==='true') {recoveryCalls++;return pending;}
    return page([old,other]);
  });
  const upload=vi.spyOn(api,'upload').mockRejectedValueOnce(new ApiError(409,'VERSION_CONFLICT','합성 충돌')).mockImplementationOnce(()=>new Promise(()=>{}));
  render(<References account={account}/>);
  const {form}=await openDraft();
  await waitFor(()=>expect(recoveryCalls).toBe(1));
  expect((within(form).getByRole('button',{name:'새 버전 저장'}) as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(screen.getAllByRole('button',{name:'사진·설명 교체'})[1]);
  await act(async()=>resolve(page([{...old,id:'late-wrong-reference',version:2,state_version:1}])));
  expect((within(form).getByRole('textbox',{name:/이 사진에서 참고할 점/}) as HTMLInputElement).value).toBe('둘째 Reference');
  expect(within(form).queryByText('최신 Reference v2를 확인했습니다.')).toBeNull();
  fireEvent.change(within(form).getByRole('textbox',{name:/변경 사유/}),{target:{value:'둘째 대상 변경'}});
  fireEvent.click(within(form).getByRole('button',{name:'새 버전 저장'}));
  await waitFor(()=>expect(upload).toHaveBeenCalledTimes(2));
  expect(upload.mock.calls[1][0]).toBe('/references/reference-other');
  expect(upload.mock.calls[1][1]).toEqual({state_version:1,caption:'둘째 Reference',reason:'둘째 대상 변경'});
  expect(upload.mock.calls[1][2]).toEqual([]);
});
