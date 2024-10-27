import "./App.css";
import { useState, useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react"; // Ensure you have this import

function App() {
  const {
    loginWithRedirect,
    logout,
    user,
    isAuthenticated,
    getAccessTokenSilently,
    isLoading,
  } = useAuth0(); // Hook usage here is correct

  const BASE_URL = "http://127.0.0.1:8000/";

  const handleLogout = () => {
    logout({ returnTo: window.location.origin });
  };

  const handleLogin = () => {
    loginWithRedirect();
  };

  const logToken = async () => {
    const token = await getAccessTokenSilently();
    console.log(token);
  };

  if (isLoading) {
    return <div>Loading ...</div>;
  }

  return (
    <div>
      <h1>Welcome to My App</h1>
      {isAuthenticated ? (
        <div>
          <h2>Hello, {user.name}</h2>
          <button onClick={handleLogout}>Logout</button>
          <button onClick={logToken}>Log Token</button>
          <div>
            <h1>{user.name}</h1>
            <h2>{user.email}</h2>
          </div>
        </div>
      ) : (
        <div>
          <button onClick={handleLogin}>Login</button>
          <button onClick={logToken}>Log Token</button>
        </div>
      )}
    </div>
  );
}

export default App;
