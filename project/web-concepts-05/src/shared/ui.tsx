import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { api, ApiError, queryString, type AccountMe, type Page } from '@storeloop/api-client';
import { errorRoute, filterParams, statusLabel, homeFor } from './policy';
export { api, queryString };
export type Row = Record<string, any>;
export type { Page };
type Session = {
    account: AccountMe;
    location: string;
    refreshIdentity: () => Promise<void>;
    security: (error: unknown) => void;
};
export const SessionContext = createContext<Session>(null!);
export const useSession = () => useContext(SessionContext);
export function go(path: string, replace = false) { if (!path.startsWith('/') || path.startsWith('//'))
    return; history[replace ? 'replaceState' : 'pushState']({}, '', path); window.dispatchEvent(new PopStateEvent('popstate')); }
export function Link({ to, children, ...rest }: React.AnchorHTMLAttributes<HTMLAnchorElement> & {
    to: string;
}) { return <a {...rest} href={to} onClick={e => { rest.onClick?.(e); if (!e.defaultPrevented && !e.ctrlKey && !e.metaKey && !e.shiftKey && e.button === 0) {
    e.preventDefault();
    go(to);
} }}>{children}</a>; }
export function useLocation() { const [location, setLocation] = useState(window.location.pathname + window.location.search); useEffect(() => { const change = () => setLocation(window.location.pathname + window.location.search); window.addEventListener('popstate', change); return () => window.removeEventListener('popstate', change); }, []); return location; }
export function useData<T = Row>(path: string | null, poll = false) { const session = useContext(SessionContext); const [state, setState] = useState<{
    data: T | null;
    error: unknown;
    loading: boolean;
}>({ data: null, error: null, loading: !!path }); const [revision, setRevision] = useState(0); const current = useRef(path); current.current = path; const refresh = () => setRevision(x => x + 1); useEffect(() => { let alive = true, timer: ReturnType<typeof setTimeout> | undefined; setState(s => ({ data: s.data, error: null, loading: !!path })); if (!path) {
    setState({ data: null, error: null, loading: false });
    return;
} const read = async () => { try {
    const data = await api.get<T>(path);
    if (!alive || current.current !== path)
        return;
    setState({ data, error: null, loading: false });
    if (poll) {
        const d = data as Row;
        const status = d.job?.status ?? d.status;
        if (!['succeeded', 'failed'].includes(status))
            timer = setTimeout(read, 2000);
    }
}
catch (error) {
    if (alive) {
        session?.security(error);
        setState({ data: null, error, loading: false });
    }
} }; read(); const visible = () => { if (!document.hidden)
    read(); }; if (poll)
    document.addEventListener('visibilitychange', visible); return () => { alive = false; if (timer)
    clearTimeout(timer); document.removeEventListener('visibilitychange', visible); }; }, [path, revision, poll]); return { ...state, refresh }; }
export function Notice({ children, tone = 'info' }: {
    children: React.ReactNode;
    tone?: string;
}) { return <div className={`notice ${tone}`}>{children}</div>; }
export function ErrorBox({ error, retry, focus = false }: {
    error: unknown;
    retry?: () => void;
    focus?: boolean;
}) { const target = useRef<HTMLDivElement>(null); useEffect(() => { if (error && focus)
    target.current?.focus(); }, [error, focus]); if (!error)
    return null; const e = error instanceof ApiError ? error : new ApiError(0, 'ERROR', '연결을 확인한 뒤 다시 시도해 주세요.'); return <div role="alert" className="notice error" tabIndex={-1} ref={target}><strong>{e.message}</strong>{e.code === 'CSRF_INVALID' && <p>보안 확인이 갱신되었습니다. 입력은 유지됩니다. 버튼을 다시 눌러 요청해 주세요.</p>}{e.status === 409 && <p>최신 상태를 다시 확인했습니다. 작성한 내용은 유지됩니다. 변경 내용을 확인한 뒤 저장해 주세요.</p>}{e.details.map((v, i) => <p key={i}>{v.field}: {v.message}</p>)}{e.requestId && <small>요청 번호 {e.requestId}</small>}{retry && <button onClick={retry} type="button">다시 조회</button>}</div>; }
export function Load({ query, children }: {
    query: ReturnType<typeof useData<any>>;
    children: (data: any) => React.ReactNode;
}) { return <>{query.loading && <p role="status">{query.data ? '탐색 결과 갱신 중…' : '자료를 불러오는 중…'}</p>}<ErrorBox error={query.error} retry={query.refresh}/>{query.data && children(query.data)}</>; }
export function useAction(onConflict?: () => void | Promise<void>) { const session = useContext(SessionContext); const [busy, setBusy] = useState(false), [error, setError] = useState<unknown>(null), [message, setMessage] = useState(''); const lock = useRef(false); const run = async (action: () => Promise<unknown>, success = '변경을 저장했습니다.') => { if (lock.current)
    return false; lock.current = true; setBusy(true); setError(null); setMessage(''); try {
    await action();
    setMessage(success);
    return true;
}
catch (e) {
    session?.security(e);
    if (e instanceof ApiError && e.status === 409) {
        try {
            await onConflict?.();
        }
        catch (reloadError) {
            session?.security(reloadError);
            setError(reloadError);
            return false;
        }
    }
    setError(e);
    return false;
}
finally {
    lock.current = false;
    setBusy(false);
} }; return { run, busy, error, message, feedback: <><ErrorBox error={error} focus/>{message && <p role="status" className="notice success">{message}</p>}</> }; }
export function Field({ label, name, value, onChange, type = 'text', required = false, options, children, maxLength, minLength, disabled = false }: {
    label: string;
    name: string;
    value: any;
    onChange: (v: string) => void;
    type?: string;
    required?: boolean;
    options?: {
        value: string;
        label: string;
    }[];
    children?: React.ReactNode;
    maxLength?: number;
    minLength?: number;
    disabled?: boolean;
}) { const id = React.useId(); return <div className="field"><label htmlFor={id}>{label}{required ? ' *' : ''}</label>{options ? <select id={id} aria-describedby={children ? id + '-help' : undefined} name={name} value={value ?? ''} onChange={e => onChange(e.target.value)} required={required} disabled={disabled}>{options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}</select> : type === 'textarea' ? <textarea id={id} aria-describedby={children ? id + '-help' : undefined} name={name} value={value ?? ''} onChange={e => onChange(e.target.value)} maxLength={maxLength} required={required} disabled={disabled}/> : <input id={id} aria-describedby={children ? id + '-help' : undefined} name={name} type={type} value={value ?? ''} onChange={e => onChange(e.target.value)} required={required} maxLength={maxLength} minLength={minLength} disabled={disabled} autoComplete={type === 'password' ? 'new-password' : undefined}/>} {children && <small id={id + '-help'}>{children}</small>}</div>; }
export const choices = (rows: Row[] = [], empty = '전체') => [{ value: '', label: empty }, ...rows.map(r => ({ value: r.id, label: r.name ?? r.display_name ?? r.title }))];
export function Badge({ value, label }: {
    value: string;
    label?: string;
}) { return <span className={`badge ${value}`}>{label ?? statusLabel(value)}</span>; }
export function Empty({ children = '조건에 맞는 항목이 없습니다.' }: {
    children?: React.ReactNode;
}) { return <div className="empty">{children}</div>; }
export function Pager({ data }: {
    data: Page<unknown>;
}) { const location = useLocation(); const move = (page: number) => { const url = new URL(location, window.location.origin); url.searchParams.set('page', String(page)); go(url.pathname + url.search); }; return <div className="pager"><span>{data.total}건 · {data.page}페이지</span><button disabled={data.page <= 1} onClick={() => move(data.page - 1)}>이전</button><button disabled={data.page * data.page_size >= data.total} onClick={() => move(data.page + 1)}>다음</button></div>; }
export function Table({ caption, head, children }: {
    caption: string;
    head: string[];
    children: React.ReactNode;
}) { return <div className="table-scroll" role="region" aria-label={caption} tabIndex={0}><table><caption>{caption}</caption><thead><tr>{head.map(h => <th key={h} scope="col">{h}</th>)}</tr></thead><tbody>{children}</tbody></table></div>; }
export function useOptions(operator = false) { const stores = useData<Page<Row>>(operator ? '/operations/stores?page_size=100' : '/stores?page_size=100'); const categories = useData<Page<Row>>(operator ? '/operations/categories?page_size=100' : '/categories?page_size=100'); return { stores, categories }; }
export function pageQuery(extra: Row = {}, withFilters = true) { const p = new URLSearchParams(window.location.search); const params = withFilters ? filterParams(p.toString()) : new URLSearchParams(); params.set('page', p.get('page') ?? '1'); params.set('page_size', '12'); Object.entries(extra).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '')
    params.set(k, String(v)); }); return '?' + params.toString(); }
export function backLink(fallback: string) { const back = new URLSearchParams(window.location.search).get('return'); if (!back || !back.startsWith('/') || back.startsWith('//'))
    return fallback; try {
    const target = new URL(back, window.location.origin);
    const prefix = fallback.split('/').slice(0, 2).join('/');
    return target.origin === window.location.origin && (target.pathname === prefix || target.pathname.startsWith(prefix + '/')) ? target.pathname + target.search : fallback;
}
catch {
    return fallback;
} }
export function detailLink(path: string) { return path + queryString({ return: window.location.pathname + window.location.search }); }
export function ScopeExplorer({ children, title, dates = true }: {
    children: React.ReactNode;
    title: string;
    dates?: boolean;
}) { const { account } = useSession(); const { stores, categories } = useOptions(); const location = useLocation(); const search = new URLSearchParams(location.split('?')[1]); const [draft, setDraft] = useState<Row>(Object.fromEntries(filterParams(search.toString()))); const [copied, setCopied] = useState(''); useEffect(() => setDraft(Object.fromEntries(filterParams(search.toString()))), [location]); const regions = Array.from(new Map((stores.data?.items ?? []).map(s => [s.region_id, { id: s.region_id, name: s.region_name }])).values()); return <div className="workspace"><aside className="explorer"><details open={window.innerWidth > 720}><summary>범위 탐색</summary><p className="muted">{account.role === 'hq' ? '전체 매장' : account.role === 'regional' ? '소속 지역' : account.role === 'ofc' ? '담당 매장' : '연결 매장'}</p><ErrorBox error={stores.error} retry={stores.refresh}/><form onSubmit={e => { e.preventDefault(); go(window.location.pathname + queryString(draft)); }}><Field label="지역" name="region_id" value={draft.region_id} onChange={v => setDraft({ ...draft, region_id: v, store_id: '' })} options={choices(regions)}/><Field label="매장" name="store_id" value={draft.store_id} onChange={v => setDraft({ ...draft, store_id: v })} options={choices((stores.data?.items ?? []).filter(s => !draft.region_id || s.region_id === draft.region_id))}/><Field label="카테고리" name="category_id" value={draft.category_id} onChange={v => setDraft({ ...draft, category_id: v })} options={choices(categories.data?.items)}/>{dates && <><Field label="시작일" name="date_from" type="date" value={draft.date_from} onChange={v => setDraft({ ...draft, date_from: v })}/><Field label="종료일" name="date_to" type="date" value={draft.date_to} onChange={v => setDraft({ ...draft, date_to: v })}/><small>조회 기준: UTC 날짜<br />화면 시각: Asia/Seoul</small></>}<Field label="매장 상태" name="is_active" value={draft.is_active} onChange={v => setDraft({ ...draft, is_active: v })} options={[{ value: '', label: '전체' }, { value: 'true', label: '활성' }, { value: 'false', label: '비활성' }]}/><button className="primary">탐색 조건 적용</button><button type="button" onClick={() => go(window.location.pathname)}>필터 초기화</button></form><button type="button" onClick={async () => { try {
    await navigator.clipboard.writeText(window.location.href);
    setCopied('현재 탐색 주소를 복사했습니다.');
}
catch {
    setCopied('주소창의 현재 주소를 복사해 주세요.');
} }}>현재 탐색 주소 복사</button><p role="status">{copied}</p></details></aside><section className="work-area"><div className="breadcrumb">{homeFor(account.role).slice(1)} / {title}</div>{children}</section></div>; }
