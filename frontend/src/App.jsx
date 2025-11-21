import { useState } from "react";
import LoginPage from "./pages/LoginPage";
import DashboardTA from "./pages/DashboardTA";
import DashboardStudent from "./pages/DashboardStudent";

function App() {
  const [user, setUser] = useState(null); // { id, role }

  if (!user) return <LoginPage onLogin={setUser} />;

  return user.role === "ta" ? (
    <DashboardTA user={user} onLogout={() => setUser(null)} />
  ) : (
    <DashboardStudent user={user} onLogout={() => setUser(null)} />
  );
}

export default App;
