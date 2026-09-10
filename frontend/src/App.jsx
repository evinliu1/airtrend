import { useState } from "react";
import Locations from "./Locations.jsx";
import Trends from "./Trends.jsx";

export default function App() {
  const [view, setView] = useState("trends");

  return (
    <div>
      <nav>
        <button onClick={() => setView("trends")}>Trends</button>
        <button onClick={() => setView("locations")}>Stations</button>
      </nav>

      {view === "trends" ? <Trends /> : <Locations />}
    </div>
  );
}
