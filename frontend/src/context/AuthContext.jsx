import { createContext, useContext, useEffect, useState } from "react";
import {
  getCurrentUser,
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
  updateLanguage as apiUpdateLanguage,
} from "../api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .finally(() => setLoading(false));
  }, []);

  async function login(credentials) {
    const u = await apiLogin(credentials);
    setUser(u);
    return u;
  }

  async function register(details) {
    const u = await apiRegister(details);
    setUser(u);
    return u;
  }

  async function logout() {
    await apiLogout();
    setUser(null);
  }

  async function setLanguage(language) {
    const u = await apiUpdateLanguage({ language });
    setUser(u);
    return u;
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, setLanguage }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}