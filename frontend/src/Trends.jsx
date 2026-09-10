import { useEffect, useState } from "react";

export default function Trends() {
  const [rows, setRows] = useState([]);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);
  const [direction, setDirection] = useState("worsening");
  const [minR2, setMinR2] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("per_page", "20");
    params.set("page", String(page));
    params.set("min_r2", String(minR2));
    if (direction) params.set("direction", direction);
    params.set("order", direction === "imporving" ? "asc" : "desc");

    fetch(`http://localhost:8000/api/trends?${params}`)
      .then((r) => {
        if (!r.ok) throw new Error(`status ${r.status}`);
        return r.json();
      })
      .then((body) => {
        setRows(body.data);
        setTotal(body.total);
        setTotalPages(body.total_pages || 1);
        setStatus("ready");
      })
      .catch((err) => {
        setError(err.message);
        setStatus("error");
      });
  }, [direction, minR2, page]);

  return (
    <main>
      <h1>Where is air quality changing?</h1>

      <select
        value={direction}
        onChange={(e) => {
          setDirection(e.target.value);
          setPage(1);
        }}
      >
        <option value="worsening">getting worse</option>
        <option value="improving">getting better</option>
        <option value="">all</option>
      </select>

      <select
        value={minR2}
        onChange={(e) => {
          setMinR2(e.target.value);
          setPage(1);
        }}
      >
        <option value={0}>any fit</option>
        <option value={0.3}>r2 over 0.3</option>
        <option value={0.6}>r2 over 0.6</option>
      </select>

      {status === "loading" && <p>loading...</p>}
      {status === "error" && <p>could not load. {error}</p>}
      {status === "ready" && rows.length === 0 && <p>no stations match.</p>}
      {status === "ready" && rows.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Station</th>
              <th>Slope (ug/m3 per year)</th>
              <th>Avg</th>
              <th>Fit</th>
              <th>Years</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.location_id}>
                <td>{row.name}</td>
                <td style={{ color: row.slope > 0 ? "crimson" : "green" }}>
                  {row.slope > 0 ? "+" : ""}
                  {row.slope.toFixed(3)}
                </td>
                <td>{row.mean_value?.toFixed(1)}</td>
                <td>{row.r2?.toFixed(2)}</td>
                <td>
                  {row.years_used} ({row.first_year}-{row.last_year})
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div>
        <button disabled={page <= 1} onClick={() => setPage(page - 1)}>
          prev
        </button>
        <span>
          page {page} of {totalPages} - {total} stations
        </span>
        <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
          next
        </button>
      </div>
    </main>
  );
}
