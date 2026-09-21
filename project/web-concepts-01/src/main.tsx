import React from 'react';
import {createRoot,type Root} from 'react-dom/client';
import {BrowserRouter} from 'react-router-dom';
import {QueryClientProvider} from '@tanstack/react-query';
import {createAppQueryClient} from './app/query-client';
import {App} from './app/App';
import './styles.css';
const client=createAppQueryClient();
// HMR이 진입점을 다시 평가해도 같은 DOM에는 기존 React root를 재사용한다.
const rootKey = Symbol.for("storeloop.concept-01.react-root");
const container = document.getElementById("root") as (HTMLElement & { [rootKey]?: Root }) | null;
if (container) {
  const root = container[rootKey] ?? (container[rootKey] = createRoot(container));
  root.render(<React.StrictMode><QueryClientProvider client={client}><BrowserRouter><App/></BrowserRouter></QueryClientProvider></React.StrictMode>);
}
