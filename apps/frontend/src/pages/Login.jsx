import { useState } from "react";
import { LockKeyhole, LogIn, UserRound } from "lucide-react";

import { login } from "../services/authApi";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const session = await login({ username, password });
      onLogin(session);
    } catch (requestError) {
      setError(requestError.message || "Đăng nhập không thành công");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 flex items-center justify-center px-4 py-8">
      <section className="w-full max-w-sm bg-white border border-slate-200 rounded-lg shadow-sm p-5">
        <div className="mb-5">
          <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-100 flex items-center justify-center mb-3">
            <LockKeyhole size={20} className="text-blue-600" />
          </div>
          <h1 className="text-lg font-bold text-slate-900">Calculus AI</h1>
          <p className="text-sm text-slate-500 mt-1">
            Hãy đăng nhập bằng tài khoản được cấp để sử dụng ứng dụng.
          </p>
        </div>

        <form className="space-y-3" onSubmit={handleSubmit}>
          <label className="block">
            <span className="text-xs font-semibold text-slate-600">Username</span>
            <div className="mt-1 flex items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 focus-within:border-blue-400 focus-within:bg-white">
              <UserRound size={16} className="text-slate-400" />
              <input
                className="w-full bg-transparent text-sm text-slate-800 outline-none"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                autoComplete="username"
                required
              />
            </div>
          </label>

          <label className="block">
            <span className="text-xs font-semibold text-slate-600">Password</span>
            <div className="mt-1 flex items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 focus-within:border-blue-400 focus-within:bg-white">
              <LockKeyhole size={16} className="text-slate-400" />
              <input
                className="w-full bg-transparent text-sm text-slate-800 outline-none"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
              />
            </div>
          </label>

          {error && (
            <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
              {error}
            </div>
          )}

          <button
            className="w-full inline-flex items-center justify-center gap-2 rounded-md bg-blue-600 px-3 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            disabled={loading}
          >
            <LogIn size={16} />
            {loading ? "Đang đăng nhập" : "Đăng nhập"}
          </button>
        </form>

        <div className="mt-4 rounded-md bg-slate-50 border border-slate-200 px-3 py-2 text-xs text-slate-500">
          Demo: admin/Admin@123 hoac user1/User@123.
        </div>
      </section>
    </main>
  );
}

