
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import EventCard from '../components/EventCard';
import { api, toResult } from "../lib/apiClient";

export default function Events() {
  const [filters, setFilters] = useState({
    keyword: '',
    location: '',
    startDate: '',
    endDate: '',
  });
  const [events, setEvents] = useState([]);
  const [locations, setLocations] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/events/events', {
      params: filters,
      withCredentials: true
    })
      .then(res => setEvents(res.data))
      .catch(() => setError('Failed to load events.'));
  }, [filters]);

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/events/filter_events')
      .then(res => setLocations(res.data))
      .catch(err => console.error('Error fetching locations', err));
  }, []);

  const handleChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const clearFilters = () => {
    setFilters({ keyword: '', location: '', startDate: '', endDate: '' });
  };

  return (
    <div className="events-wrapper">
      <div className="card large-card" role="region" aria-label="Discover Events">
        <div className="filter-panel">
          <h1 className="brand-gradient">Discover Events</h1>
          <p className="filter-tagline">Turn your free time into something extraordinary—start by searching through upcoming events below.</p>

          <form className="filter-grid" noValidate onSubmit={(e) => e.preventDefault()}>
            {/* Search */}
            <div className="input-wrapper">
              <span className="icon">🔍</span>
              <input
                name="keyword"
                placeholder="Search"
                value={filters.keyword}
                onChange={handleChange}
              />
            </div>

            {/* Location */}
            <div className="input-wrapper">
              <span className="icon">📍</span>
              <select name="location" value={filters.location} onChange={handleChange}>
                <option value="">All Locations</option>
                {locations.map((loc, index) => (
                  <option key={index} value={loc.city}>{loc.city}</option>
                ))}
              </select>
            </div>

            {/* Start Date */}
            <div className="input-wrapper">
              <label htmlFor='startDate' className="filter-label">Start Date</label>
              <input
                name="startDate"
                type="date"
                placeholder="Start Date"
                value={filters.startDate}
                onChange={handleChange}
              />
            </div>

            {/* End Date */}
            <div className="input-wrapper">
              <label htmlFor="endDate" className="filter-label">End Date</label>
              <input
                name="endDate"
                type="date"
                placeholder="End Date"
                value={filters.endDate}
                onChange={handleChange}
              />
            </div>
          </form>
                  <div className="clear-filters">
                      <button type="button" className="clear-button" onClick={clearFilters}>
                        Clear Filters
                      </button>
                  </div>
        </div>

        {error && <div className="error" role="alert">{error}</div>}

        <div className="event-list">
          {events.length > 0 ? (
            events.map((event, index) => (
              <EventCard key={event.ID ? `${event.ID}-${index}` : `event-${index}`} event={event} />
            ))
          ) : (
            <p>No events found.</p>
          )}
        </div>
      </div>
    </div>
  );
}