import { useEffect, useState } from "react";
import EventCard from './components/EventCard';


function App() {
  const [apiMsg, setApiMsg] = useState("…checking API");

  useEffect(() => {
    fetch("http://localhost:5000/health")
      .then((r) => r.json())
      .then((d) => setApiMsg(d.status || "OK"))
      .catch(() => setApiMsg("API not reachable"));
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", padding: 24 }}>
      <h1>OneSky</h1>
      <p>Frontend is running ✅</p>
      <p>Backend health: <strong>{apiMsg}</strong></p>
    </div>
  );
}

export default App;
