import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { Auth0Provider } from "@auth0/auth0-react";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <Auth0Provider
      domain="dev-2anuorhsrl8w0pl6.us.auth0.com"
      clientId="QOI0vpZ7AMuhXaGqR0xUv4pvITJLVUe7"
      redirectUri={window.location.origin}
      audience="http://127.0.0.1:8000/"
      scope="openid profile email"
    >
      <App />
    </Auth0Provider>
  </React.StrictMode>
);
