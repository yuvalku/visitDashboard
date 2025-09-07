import React, { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000";

function App() {
  const [categories, setCategories] = useState([]);
  const [dmas, setDmas] = useState([]);
  const [visits, setVisits] = useState([]);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [totalPages, setTotalPages] = useState(1);

  // Filters
  const [filters, setFilters] = useState({
    start_date: "",
    end_date: "",
    poi_name: "",
    poi_category: "",
    dma: "",
    search: ""
  });
  

  // Load categories & DMAs at start
  useEffect(() => {
    axios.get(`${API_BASE}/categories`).then(res => setCategories(res.data));
    axios.get(`${API_BASE}/dmas`).then(res => setDmas(res.data));
  }, []);

  // Fetch visits whenever page or filters change
  useEffect(() => {
    fetchVisits();
  }, [page, perPage]);

  const fetchVisits = () => {
    axios
      .get(`${API_BASE}/visits`, {
        params: { page, per_page: perPage, ...filters }
      })
      .then(res => {
        setVisits(res.data.data);
        setTotalPages(res.data.pages);
      })
      .catch(err => console.error("Error fetching visits:", err));
  };

  const handleFilterChange = e => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const handleSearch = () => {
    setPage(1); // Reset to first page
    fetchVisits();
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Visits Dashboard</h1>


      {/* Filters */}
      <div style={{ marginBottom: "20px" }}>
        <input
          type="date"
          name="start_date"
          value={filters.start_date}
          onChange={handleFilterChange}
        />
        <input
          type="date"
          name="end_date"
          value={filters.end_date}
          onChange={handleFilterChange}
        />
        <input
          type="text"
          name="poi_name"
          placeholder="POI Name"
          value={filters.poi_name}
          onChange={handleFilterChange}
        />
        <select
          name="poi_category"
          value={filters.poi_category}
          onChange={handleFilterChange}
        >
          <option value="">All Categories</option>
          {categories.map((c, idx) => (
            <option key={idx} value={c}>
              {c}
            </option>
          ))}
        </select>
        <select
          name="dma"
          value={filters.dma}
          onChange={handleFilterChange}
        >
          <option value="">All DMAs</option>
          {dmas.map((d, idx) => (
            <option key={idx} value={d}>
              {d}
            </option>
          ))}
        </select>
        <input
          type="text"
          name="search"
          placeholder="Search POI"
          value={filters.search}
          onChange={handleFilterChange}
        />
        <button onClick={handleSearch}>Search</button>
      </div>

      {/* Table */}
      <table border="1" cellPadding="5" style={{ width: "100%" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Date</th>
            <th>POI Name</th>
            <th>Category</th>
            <th>DMA</th>
            <th>Visits</th>
          </tr>
        </thead>
        <tbody>
          {visits.map((v) => (
            <tr key={v.id}>
              <td>{v.id}</td>
              <td>{v.date}</td>
              <td>{v.poi_name}</td>
              <td>{v.poi_category}</td>
              <td>{v.dma}</td>
              <td>{v.visits}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination */}
      <div style={{ marginTop: "10px" }}>
        <button disabled={page === 1} onClick={() => setPage(page - 1)}>
          Previous
        </button>
        <span> Page {page} of {totalPages} </span>
        <button disabled={page === totalPages} onClick={() => setPage(page + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}

export default App;
