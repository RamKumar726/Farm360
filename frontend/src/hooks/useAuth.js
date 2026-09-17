import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { authAPI } from "../config/api";
import useAppStore from "../store/useAppStore";
import { getDefaultRoute } from "../config/roleRoutes";

export function useAuth() {
  const { user, isAuthenticated, setUser, clearUser } = useAppStore();
  const navigate = useNavigate();

  const login = async (email, password) => {
    const res = await authAPI.login({ email, password });
    if (res.success) {
      setUser(res.data);
      navigate(getDefaultRoute(res.data.role));
    }
    return res;
  };

  const logout = async () => {
    await authAPI.logout();
    clearUser();
    navigate("/login");
  };

  const checkAuth = async () => {
    try {
      const res = await authAPI.me();
      if (res.success) setUser(res.data);
    } catch {
      clearUser();
    }
  };

  return { user, isAuthenticated, login, logout, checkAuth };
}
