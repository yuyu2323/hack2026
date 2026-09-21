import {createContext,useContext,type ReactNode} from 'react';
import {type AccountMe} from '@storeloop/api-client';
export const SessionContext=createContext<{account:AccountMe;logout:()=>void}|null>(null);
export function useSession(){const value=useContext(SessionContext);if(!value)throw new Error('로그인이 필요합니다.');return value;}
export function SessionProvider({account,logout,children}:{account:AccountMe;logout:()=>void;children:ReactNode}){return <SessionContext.Provider value={{account,logout}}>{children}</SessionContext.Provider>;}
