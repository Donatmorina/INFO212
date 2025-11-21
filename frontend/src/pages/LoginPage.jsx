import { useState } from "react";
import axios from "axios";
import RegisterPage from "./RegisterPage";

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [showRegister, setShowRegister] = useState(false);

  if (showRegister) {
    return <RegisterPage onBackToLogin={() => setShowRegister(false)} />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await axios.post("http://127.0.0.1:5000/api/login", {
        username,
        password,
      });
      if (res.data.success) {
        onLogin({ id: res.data.user_id, role: res.data.role });
      }
    } catch (err) {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white shadow-md rounded-xl p-8 w-full max-w-md">
        <h1 className="text-2xl font-semibold text-center mb-6">Login</h1>
        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Username"
            className="w-full border rounded-lg p-2"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full border rounded-lg p-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700"
          >
            Login
          </button>
        </form>
        <button
          onClick={() => setShowRegister(true)}
          className="mt-4 text-blue-600 hover:underline w-full text-center"
        >
          Create an account
        </button>
      </div>
    </div>
  );
}
