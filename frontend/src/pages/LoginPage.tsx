import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authService } from "../services/authService";

interface LoginPageProps {
  onLogin: () => Promise<void>;
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authService.login(email, password);
      await onLogin();
      navigate("/");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4 bg-gray-50/50">
      <div className="w-full max-w-sm">
        <div className="text-center mb-10">
          <h1 className="text-gray-900 text-3xl font-black tracking-tight">
            Shop<span className="text-[#e8c547]">Ease</span>
          </h1>
          <p className="text-gray-500 text-sm mt-2">Sign in to your account</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white border border-gray-100 rounded-3xl p-8 space-y-5 shadow-xl shadow-gray-200/50"
        >
          {error && (
            <div className="bg-red-50 border border-red-100 text-red-600 text-xs font-medium px-4 py-3 rounded-xl animate-shake">
              {error}
            </div>
          )}

          <div>
            <label className="block text-gray-700 text-xs font-semibold uppercase tracking-wider mb-2 ml-1">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-[#e8c547]/50 focus:border-[#e8c547] transition-all placeholder:text-gray-400"
              placeholder="name@company.com"
            />
          </div>

          <div>
            <label className="block text-gray-700 text-xs font-semibold uppercase tracking-wider mb-2 ml-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-[#e8c547]/50 focus:border-[#e8c547] transition-all placeholder:text-gray-400"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gray-900 text-white font-bold py-3.5 rounded-xl hover:bg-gray-800 active:scale-[0.98] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-gray-900/10"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Processing...
              </span>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        <p className="text-center text-gray-500 text-sm mt-6">
          Don't have an account?{" "}
          <Link
            to="/register"
            className="text-gray-900 font-bold hover:text-[#d4b43c] transition-colors"
          >
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
