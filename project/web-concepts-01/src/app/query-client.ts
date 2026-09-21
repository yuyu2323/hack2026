import {QueryClient,QueryCache,MutationCache} from '@tanstack/react-query';
import {ApiError} from '@storeloop/api-client';

export function handleAuthError(error:unknown){
 if(error instanceof ApiError&&(error.status===401||(error.status===403&&error.code!=='CSRF_INVALID'))){window.dispatchEvent(new Event('storeloop:auth'));return true;}
 return false;
}
export function createAppQueryClient(){
 const onError=handleAuthError;
 return new QueryClient({queryCache:new QueryCache({onError:(error,query)=>{if(query.queryKey[0]!=='session')onError(error);}}),mutationCache:new MutationCache({onError}),defaultOptions:{queries:{staleTime:5000,retry:false},mutations:{retry:false}}});
}
