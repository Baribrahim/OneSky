import React, { useState, useEffect } from "react";
import axios from "axios";
import {api, toResult} from '../lib/apiClient.js';

function SearchFilters({ onFilterSubmit }) {
  const [keyword, setKeyword] = useState('');
  const [location, setLocation] = useState('');
  const [date, setDate] = useState('');
  const [locations, setLocations] = useState([]);
  const [allData, setAllData] = useState([]);
 // const {data, error} = await toResult(api.get("/events/filter_events"))
    // setAllData(data)
    // console.log("data")
    // console.log(data)


// Fetch locations from Flask backend
  useEffect(() => {
    axios.get("http://127.0.0.1:5000/events/filter_events")
      .then(response => setLocations(response.data))
      .catch(error => console.error("Error fetching locations:", error));
  }, []);


// Submission handler
  const handleSubmit = (e) => {
    e.preventDefault();
    onFilterSubmit({ keyword, location, date });
  };

  return (
    <form onSubmit={handleSubmit}>
{/* Keyword Search */}
      <input
        type="text"
        placeholder="Search by keyword..."
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
      />
{/* Location Drop down */}
      <select value={location} onChange={(e) => setLocation(e.target.value)}>
        <option value="">All Locations</option>
        {locations.map((loc, index) => (
            <option key={index} value={loc}>{loc}</option>
        ))}
      </select>
{/* Date picker */}
      <input
        type="date"
        value={date}
        onChange={(e) => setDate(e.target.value)}
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default SearchFilters;
