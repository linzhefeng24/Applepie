import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import {AuthGate} from "./auth/AuthGate";
import { App } from "./App";
import "./index.css";
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthGate><App /></AuthGate>
    </BrowserRouter>
  </React.StrictMode>,
);
