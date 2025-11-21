import { useState } from "react";
import axios from "axios";

export default function RegisterPage({ onBackToLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");

    try {
      const res = await axios.post("http://127.0.0.1:5000/api/create_account", {
        username,
        password,
        role,
      });
      if (res.data.success) {
        setMessage("Account created successfully! You can now log in.");
        setUsername("");
        setPassword("");
      } else {
        setError(res.data.message || "Registration failed");
      }
    } catch (err) {
      setError("Username already exists or server error");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white shadow-md rounded-xl p-8 w-full max-w-md">
        <h1 className="text-2xl font-semibold text-center mb-6">
          Create Account
        </h1>

        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
        {message && <p className="text-green-600 text-sm mb-3">{message}</p>}

        <form onSubmit={handleRegister} className="space-y-4">
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

          <select
            className="w-full border rounded-lg p-2"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <option value="student">Student</option>
            <option value="ta">Teaching Assistant</option>
          </select>

          <button
            type="submit"
            className="w-full bg-green-600 text-white p-2 rounded-lg hover:bg-green-700"
          >
            Register
          </button>
        </form>

        <button
          onClick={onBackToLogin}
          className="mt-4 text-blue-600 hover:underline w-full text-center"
        >
          ← Back to login
        </button>
      </div>
    </div>
  );
}
