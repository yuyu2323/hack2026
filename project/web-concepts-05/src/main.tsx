import React from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { App } from './app/App';
import './styles.css';
// HMR이 진입점을 다시 평가해도 같은 DOM에는 기존 React root를 재사용한다.
const rootKey = Symbol.for("storeloop.concept-05.react-root");
const container = document.getElementById("root") as (HTMLElement & { [rootKey]?: Root }) | null;
if (container) {
  const root = container[rootKey] ?? (container[rootKey] = createRoot(container));
  root.render(<React.StrictMode><App /></React.StrictMode>);
}
