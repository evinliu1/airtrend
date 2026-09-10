import { useState } from "react";
import Locations from "./Locations.jsx";
import Trends from "./Trends.jsx";
import TrendMap from "./TrendMap.jsx";

export default function App() {
  const [view, setView] = useState("trends");

  return (
    <div>
      <nav>
        <button onClick={() => setView("trends")}>Trends</button>
        <button onClick={() => setView("locations")}>Stations</button>
        <button onClick={() => setView("map")}>Trend Map</button>
      </nav>
      {view === "trends" && <Trends />}
      {view === "locations" && <Locations />}
      {view === "map" && <TrendMap />}
    </div>
  );
}
