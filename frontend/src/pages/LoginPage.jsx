import { useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { Leaf, Eye, EyeOff, ArrowLeft } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { getDefaultRoute } from "../config/roleRoutes";
import toast from "react-hot-toast";

export default function LoginPage() {
  const { login, user, isAuthenticated } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated && user) {
    return <Navigate to={getDefaultRoute(user.role)} replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(form.email, form.password);
    } catch (err) {
      toast.error(err?.detail || err?.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-hero-gradient flex items-center justify-center p-4">
      {/* Background decorations */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-primary-600/20 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md">
        {/* Back link */}
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs text-[#8fac9a] hover:text-[#f0ede4] mb-6 transition-colors"
        >
          <ArrowLeft size={14} />
          <span>Back to Landing Page</span>
        </Link>

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-accent/20 border border-accent/30 rounded-2xl mb-4">
            <Leaf size={32} className="text-accent" />
          </div>
          <h1 className="font-display text-3xl font-bold text-[#f0ede4]">Prasad Farm</h1>
          <p className="text-gradient-gold font-semibold text-lg">Care 360°</p>
          <p className="text-[#8fac9a] text-sm mt-2">Sign in to your portal</p>
        </div>

        {/* Form card */}
        <div className="glass-panel p-8 shadow-card">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="label">Email Address</label>
              <input
                id="email"
                type="email"
                className="input"
                placeholder="you@prasadfarm.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="label">Password</label>
              <div className="relative">
                <input
                  id="password"
                  type={showPass ? "text" : "password"}
                  className="input pr-10"
                  placeholder="••••••••"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8fac9a] hover:text-[#f0ede4]"
                >
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              id="login-btn"
              type="submit"
              disabled={loading}
              className="btn-primary w-full mt-2"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-primary-900/40 border-t-primary-900 rounded-full animate-spin" />
                  Signing in...
                </span>
              ) : "Sign In"}
            </button>
          </form>

          <p className="text-center text-sm text-[#8fac9a] mt-6">
            Don't have an account?{" "}
            <Link to="/register" className="text-accent hover:underline">Register</Link>
          </p>
        </div>

        {/* Demo credentials hint */}
        <div className="mt-4 glass-panel p-4 text-xs text-[#8fac9a] text-center">
          <p>🌿 Multi-role platform: Founder · Zone Admin · Employee · Agri Officer · Farm Employee · Customer</p>
        </div>
      </div>
    </div>
  );
}
