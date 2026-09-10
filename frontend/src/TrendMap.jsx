import { useEffect, useRef, useState } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

function colorFor(slope) {
  if (slope > 0.3) return "#b2182b";
  if (slope > 0.05) return "#ef8a62";
  if (slope < -0.3) return "#2166ac";
  if (slope < -0.05) return "#67a9cf";
  return "#999999";
}

export default function TrendMap() {
  const container = useRef(null);
  const map = useRef(null);
  const markers = useRef([]);
  const [rows, setRows] = useState([]);

  useEffect(() => {
    if (map.current) return;
    map.current = new mapboxgl.Map({
      container: container.current,
      style: "mapbox://styles/mapbox/light-v11",
      center: [-98, 39],
      zoom: 3,
    });
  }, []);

  useEffect(() => {
    fetch("http://localhost:8000/api/trends?per_page=100&min_r2=0.3")
      .then((r) => r.json())
      .then((body) => setRows(body.data))
      .catch(() => setRows([]));
  }, []);

  useEffect(() => {
    if (!map.current) return;
    markers.current.forEach((m) => m.remove());
    markers.current = [];

    rows.forEach((row) => {
      const dot = document.createElement("div");
      dot.style.width = "12px";
      dot.style.height = "12px";
      dot.style.borderRadius = "50%";
      dot.style.background = colorFor(row.slope);
      dot.style.border = "1px solid white";

      const popup = new mapboxgl.Popup({ offset: 12 }).setHTML(
        `<strong>${row.name}</strong><br/>` +
          `slope ${row.slope > 0 ? "+" : ""}${row.slope.toFixed(
            3
          )} ug/m3 per year <br/>` +
          `r2 ${row.r2?.toFixed(2)} over ${row.years_used} years`
      );

      const marker = new mapboxgl.Marker(dot)
        .setLngLat([row.longitude, row.latitude])
        .setPopup(popup)
        .addTo(map.current);

      markers.current.push(marker);
    });
  }, [rows]);

  return <div ref={container} style={{ width: "100%", height: "600px" }} />;
}
