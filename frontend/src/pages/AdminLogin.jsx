import { useState } from "react";
import { LockKeyhole, LogIn, ShieldCheck } from "lucide-react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { isAdminLoggedIn, loginAdmin } from "../services/adminAuthApi";

export default function AdminLogin() {
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (isAdminLoggedIn()) {
    return <Navigate replace to="/admin-knowledge" />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      await loginAdmin(username.trim(), password);
      navigate(location.state?.from?.pathname || "/admin-knowledge", {
        replace: true,
      });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Login admin gagal."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-120px)] items-center justify-center rounded-3xl bg-[#FFF7ED] p-4 sm:p-6">
      <section className="card w-full max-w-[460px] p-6 sm:p-8">
        <div className="flex items-start gap-4">
          <div className="rounded-2xl bg-baliCream p-3 text-baliBrown">
            <ShieldCheck size={28} />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-baliDark">Login Admin</h2>
            <p className="mt-2 text-sm leading-7 text-gray-500">
              Masuk sebagai admin untuk mengelola upload knowledge.
            </p>
          </div>
        </div>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="mb-3 block font-semibold text-baliDark">
              Username
            </label>
            <input
              className="input"
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </div>

          <div>
            <label className="mb-3 flex items-center gap-2 font-semibold text-baliDark">
              <LockKeyhole size={18} />
              Password
            </label>
            <input
              className="input"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          {error && (
            <div className="rounded-2xl bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            className="btn-primary flex w-full items-center justify-center gap-2 disabled:opacity-60"
            type="submit"
            disabled={loading}
          >
            <LogIn size={18} />
            {loading ? "Memeriksa..." : "Masuk Admin"}
          </button>
        </form>
      </section>
    </div>
  );
}
