import React, { useEffect, useRef, useState } from 'react';
import { api, ApiError, type AccountMe } from '@storeloop/api-client';
import { canVisit, errorRoute, homeFor, roleLabel } from '../shared/policy';
import { ErrorBox, Field, Link, Load, SessionContext, go, useAction, useData, useLocation, type Page, type Row } from '../shared/ui';
import { Owner } from '../store-owner/Owner';
import { Business } from '../ofc-admin/Business';
import { Platform } from '../platform-admin/Platform';
const menus = { store_owner: [['', '이력 탐색'], ['/submit', '사진 제출'], ['/issues', '확인 문의'], ['/notifications', '내 알림']], business: [['', '매장 비교'], ['/stores', '매장 연결'], ['/guidelines', '진열 기준'], ['/references', 'Reference'], ['/submissions', '제출 탐색'], ['/issues', '확인 이슈'], ['/analytics', '추이 비교'], ['/notifications', '내 알림']], platform_operator: [['', '상태·연결'], ['/accounts', '계정 탐색'], ['/catalogs', '기준 정보'], ['/jobs', '처리 작업'], ['/audit', '운영 이력'], ['/announcements', '공지 관리']] };
export function App() { const location = useLocation(), path = location.split('?')[0]; const [account, setAccount] = useState<AccountMe | null>(null), [initializing, setInitializing] = useState(true), [startupError, setStartupError] = useState<unknown>(null); const main = useRef<HTMLElement>(null); const security = (e: unknown) => { if (e instanceof ApiError) {
    const route = errorRoute(e.status, e.code);
    if (route) {
        setAccount(null);
        go(route, true);
    }
} }; const refreshIdentity = async () => { try {
    const user = await api.me();
    setAccount(user);
    if (path === '/')
        go(homeFor(user.role), true);
    else if (path !== '/login' && path !== '/forbidden' && !canVisit(user.role, path))
        go('/forbidden', true);
}
catch (e) {
    if (e instanceof ApiError && e.status === 401) {
        setAccount(null);
        if (path !== '/login')
            go('/login', true);
    }
    else
        throw e;
} }; useEffect(() => { refreshIdentity().catch(setStartupError).finally(() => setInitializing(false)); }, []); useEffect(() => { if (account && path !== '/login' && path !== '/forbidden')
    api.me().then(user => { if (user.role !== account.role || user.id !== account.id) {
        setAccount(null);
        go(homeFor(user.role), true);
        setAccount(user);
    }
    else
        setAccount(user); }).catch(security); main.current?.focus(); }, [path]); if (initializing)
    return <main className="login" role="status">접근 권한을 확인하는 중…</main>; if (startupError)
    return <main className="login"><h1>서비스에 연결할 수 없습니다</h1><ErrorBox error={startupError} retry={() => window.location.reload()}/></main>; if (path === '/forbidden' || account && !canVisit(account.role, path) && path !== '/login' && path !== '/')
    return <main className="login"><h1>접근할 수 없는 화면입니다</h1><p>현재 역할과 연결 범위에서 허용되지 않는 자료입니다.</p><Link className="button" to={account ? homeFor(account.role) : '/login'}>시작 화면으로</Link></main>; if (path === '/login' || !account)
    return <Login onLogin={user => { setAccount(user); go(homeFor(user.role), true); }}/>; if (path === '/') {
    go(homeFor(account.role), true);
    return null;
} const home = homeFor(account.role), items = account.role === 'store_owner' ? menus.store_owner : account.role === 'platform_operator' ? menus.platform_operator : menus.business; return <SessionContext.Provider value={{ account, location, refreshIdentity, security }}><a className="skip" href="#main">본문으로 바로가기</a><header className="masthead"><Link className="brand" to={home}><span className="brand-mark" aria-hidden="true">▦</span><strong>StoreLoop</strong><span>탐색과 비교</span></Link><div className="identity"><span>{account.display_name} · {roleLabel(account.role)}</span><Logout /></div></header><nav className="work-tabs" aria-label="주요 업무">{items.map(([to, label]) => <Link key={to} to={home + to} aria-current={path === home + to || (to && path.startsWith(home + to + '/')) ? 'page' : undefined}>{label}</Link>)}</nav><Announcements /><main id="main" tabIndex={-1} ref={main} key={account.id + account.role + path}>{account.role === 'store_owner' ? <Owner path={path}/> : account.role === 'platform_operator' ? <Platform path={path}/> : <Business path={path}/>}</main><footer>StoreLoop · 탐색과 비교 · 표시 시각 Asia/Seoul · 가상 매장 시연 환경</footer></SessionContext.Provider>; }
function Login({ onLogin }: {
    onLogin: (account: AccountMe) => void;
}) { const [loginId, setLoginId] = useState(''), [password, setPassword] = useState(''); const action = useAction(); return <main className="login-layout"><section className="login-story"><p className="eyebrow">STORELOOP / CONCEPT 05</p><h1>흩어진 기록을,<br />하나의 비교로.</h1><p>매장과 기준을 탐색하고<br />매대의 변화를 함께 확인하세요.</p><div className="login-grid" aria-hidden="true">{Array.from({ length: 12 }, (_, i) => <span key={i}/>)}</div></section><section className="login-form"><h2>업무 공간 로그인</h2><p>계정의 역할과 현재 연결된 범위로 시작합니다.</p><form onSubmit={async (e) => { e.preventDefault(); await action.run(async () => { const result = await api.login(loginId, password); setPassword(''); onLogin(result.account); }, '로그인했습니다.'); }}><label className="field">로그인 ID<input name="login_id" autoComplete="username" value={loginId} onChange={e => setLoginId(e.target.value)} required/></label><label className="field">비밀번호<input name="password" type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required/></label>{action.feedback}<button className="primary" disabled={action.busy}>{action.busy ? '로그인 확인 중…' : '로그인'}</button></form><small>데모 계정은 로컬 실행 안내에서 확인하세요.</small></section></main>; }
function Logout() { const action = useAction(); return <><button disabled={action.busy} onClick={() => action.run(async () => { await api.logout(); window.location.assign('/login'); }, '로그아웃했습니다.')}>로그아웃</button>{action.error && <ErrorBox error={action.error}/>}</>; }
function Announcements() { const query = useData<Page<Row>>('/announcements'); const [closed, setClosed] = useState<string[]>([]); useEffect(() => { const reload = () => query.refresh(); window.addEventListener('announcement-updated', reload); return () => window.removeEventListener('announcement-updated', reload); }, []); return <div className="announcements"><Load query={query}>{(d: Page<Row>) => d.items.filter(a => !closed.includes(a.id)).map(a => <div className="announcement" key={a.id}><div><strong>{a.title}</strong><p>{a.body}</p></div><button aria-label={a.title + ' 공지 닫기'} onClick={() => setClosed([...closed, a.id])}>닫기</button></div>)}</Load></div>; }
