import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { getMe, login as loginRequest } from "../api/auth";

const AuthContext = createContext(null);

function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem("crm_user"));
  } catch {
    return null;
  }
}

function getStoredToken() {
  return localStorage.getItem("crm_token");
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser);
  const [token, setToken] = useState(getStoredToken);
  const [loading, setLoading] = useState(Boolean(getStoredToken()));

  const logout = useCallback(() => {
    localStorage.removeItem("crm_token");
    localStorage.removeItem("crm_user");
    setToken(null);
    setUser(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    let active = true;
    window.addEventListener("crm:logout", logout);

    const token = localStorage.getItem("crm_token");
    if (!token) {
      setLoading(false);
      return () => window.removeEventListener("crm:logout", logout);
    }
    getMe()
      .then((profile) => {
        if (active) {
          localStorage.setItem("crm_user", JSON.stringify(profile));
          setUser(profile);
        }
      })
      .catch(() => {
        if (active) logout();
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
      window.removeEventListener("crm:logout", logout);
    };
  }, [logout]);

  const login = useCallback(async (credentials) => {
    const response = await loginRequest(credentials);
    localStorage.setItem("crm_token", response.access_token);
    localStorage.setItem("crm_user", JSON.stringify(response.user));
    setToken(response.access_token);
    setUser(response.user);
  }, []);

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      login,
      logout,
      isAuthenticated: Boolean(token && user),
      isManager: user?.role === "manager",
      isAgent: user?.role === "agent",
    }),
    [user, token, loading, login, logout],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
