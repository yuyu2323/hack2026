import {useCallback,useEffect,useState,useRef,createContext,useContext} from 'react';
import {api,ApiError,type AccountMe,type Page,queryString} from '@storeloop/api-client';
export {api,ApiError,queryString};
export type Row = Record<string,any>;
export type Rows = Page<Row>;
export const Session=createContext<{account:AccountMe;refresh:()=>Promise<void>}>({} as any);
export const useSession=()=>useContext(Session);
export async function checked<T>(action:Promise<T>):Promise<T>{try{return await action;}catch(e){if(e instanceof ApiError&&(e.status===401||(e.status===403&&!['CSRF_INVALID','ORIGIN_DENIED'].includes(e.code))))window.dispatchEvent(new CustomEvent('access-error',{detail:e.status}));throw e;}}
export function useData<T=Row>(path:string|null,interval=0){
 const [data,setData]=useState<T|null>(null),[error,setError]=useState<Error|null>(null),[loading,setLoading]=useState(true),[revision,setRevision]=useState(0);
 const previousPath=useRef<string|null>(null);const reload=useCallback(()=>setRevision(v=>v+1),[]);
 useEffect(()=>{let active=true;let timer:ReturnType<typeof setTimeout>;if(previousPath.current!==path)setData(null);previousPath.current=path;setError(null);setLoading(true);
 const read=async()=>{if(!path){setLoading(false);return;}try{const value=await checked(api.get<T>(path));if(active){setData(value);setError(null);}}catch(e){if(active){setData(null);setError(e as Error);}}finally{if(active){setLoading(false);if(interval)timer=setTimeout(read,interval);}}};void read();const visible=()=>{if(document.visibilityState==='visible')void read();};if(interval)document.addEventListener('visibilitychange',visible);return()=>{active=false;clearTimeout(timer);document.removeEventListener('visibilitychange',visible);};},[path,revision,interval]);
 return {data,error,loading,reload};
}
export function useAction(){const [busy,setBusy]=useState(false),[error,setError]=useState<Error|null>(null),[success,setSuccess]=useState('');const run=async<T,>(action:()=>Promise<T>,done?:(value:T)=>void)=>{if(busy)return;setBusy(true);setError(null);setSuccess('');try{const value=await checked(action());setSuccess('저장했습니다.');done?.(value);}catch(e){setError(e as Error);}finally{setBusy(false);}};return{busy,error,success,run,setError};}
