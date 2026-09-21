import {useRef} from 'react';
import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query';
import {api, queryString, ApiError, type Page} from '@storeloop/api-client';
import {useSearchParams} from 'react-router-dom';
export {api, queryString, ApiError};
// 계약 DTO는 변경 가능한 운영·업무 레코드의 공통 표시 경계에서만 유연하게 취급한다.
export type Row = Record<string, any>;
export function useData<T = Row>(path: string, interval?: number | false | ((data: T | undefined) => number | false)) {
  return useQuery<T>({queryKey:[path],queryFn:()=>api.get<T>(path),enabled:!!path,retry:false,refetchInterval:typeof interval==='function' ? q => interval(q.state.data) : interval});
}
export function useList(path: string, filters: Record<string, unknown> = {}) {return useData<Page<Row>>(path + queryString(filters));}
export function useAction<T = any>(action:(values:T)=>Promise<any>) {
  const client=useQueryClient();
  return useMutation({mutationFn:action,onSuccess:()=>client.invalidateQueries(),onError:error=>{if(error instanceof ApiError&&error.status===409)client.invalidateQueries();}});
}
export function useFilters(defaults: Record<string,string> = {}) {
  const [params,setParams]=useSearchParams();
  const values={...defaults,...Object.fromEntries(params)};
  // Router가 다음 URL을 반영하기 전 연속 입력도 직전 선택을 이어받는다.
  const latest=useRef({params,values});
  if(latest.current.params!==params)latest.current={params,values};
  const publish=(next:Record<string,string>)=>{latest.current.values=next;setParams(Object.fromEntries(Object.entries(next).filter(([,v])=>v!=='')));};
  const update=(key:string,value:string)=>{const next={...latest.current.values,[key]:value};if(key!=='page')next.page='1';publish(next);};
  const updateMany=(changes:Record<string,string>)=>publish({...latest.current.values,...changes,page:'1'});
  return {values,update,updateMany,reset:()=>{latest.current.values={...defaults};setParams({});}};
}
export function date(value?: string | null) { return value ? new Intl.DateTimeFormat('ko-KR',{dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Seoul'}).format(new Date(value)) : '—'; }
export function nullable(value: FormDataEntryValue | null) {return value ? String(value) : null;}
export function formValues(form: HTMLFormElement) {return Object.fromEntries(new FormData(form));}
