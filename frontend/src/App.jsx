import { useEffect, useState } from "react";

export default function App() {
  const [rows, setRows] = useState([]);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [parameter, setParameter] = useState("");
  const [sortBy, setSortBy] = useState("name");
  const [order, setOrder] = useState("asc");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  function handleSort(key) {
    if (key === sortBy) {
      setOrder(order === "asc" ? "desc" : "asc");
    } else {
      setSortBy(key);
      setOrder("asc");
    }
    setPage(1);
  }

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("per_page", "20");
    params.set("sort_by", sortBy);
    params.set("order", order);
    params.set("page", String(page));
    if (search) params.set("search", search);
    if (parameter) params.set("parameter", parameter);

    fetch("http://localhost:8000/api/locations?per_page=20")
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
  }, [search, parameter, sortBy, order, page]);

  if (status === "loading") return <p>loading...</p>;
  if (status === "error") return <p>could not load. {error}</p>;

  return (
    <main>
      <h1>AirTrend</h1>

      <input
        placeholder="search name"
        value={search}
        onChange={(e) => {
          setSearch(e.target.value);
          setPage(1);
        }}
      />

      <select
        value={parameter}
        onChange={(e) => {
          setParameter(e.target.value);
          setPage(1);
        }}
      >
        <option value="">all pollutants</option>
        <option value="pm25">pm25</option>
        <option value="pm10">pm10</option>
        <option value="o3">o3</option>
        <option value="no2">no2</option>
        <option value="co">co</option>
        <option value="so2">so2</option>
      </select>

      {status === "loading" && <p>loading...</p>}
      {status === "error" && <p>could not load. {error}</p>}
      {status === "ready" && (
        <table>
          <thead>
            <tr>
              <th onClick={() => handleSort("name")}>Name</th>
              <th onClick={() => handleSort("Locality")}>Locality</th>
              <th>Provider</th>
              <th>Lat</th>
              <th>Lon</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td>{row.name}</td>
                <td>{row.locality}</td>
                <td>{row.provider_name}</td>
                <td>{row.latitude.toFixed(3)}</td>
                <td>{row.longitude.toFixed(3)}</td>
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
        <button idsabled={page >= totalPages} onClick={() => setPage(page + 1)}>
          next
        </button>
      </div>
    </main>
  );
}
