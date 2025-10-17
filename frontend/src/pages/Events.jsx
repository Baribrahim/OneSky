
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SkyBrand from '../components/SkyBrand';
import EventCard from '../components/EventCard';

export default function Events() {
  const [filters, setFilters] = useState({
    keyword: '',
    location: '',
    date: '',
  });
  const [events, setEvents] = useState([]);
  const [locations, setLocations] = useState([]);
  const [error, setError] = useState('');

  // gets events when filters change
  useEffect(() => {
    axios.get('http://127.0.0.1:5000/events/events', {
      params: filters,
      withCredentials: true
    })
      .then(res => setEvents(res.data))
      .catch(err => {
        console.error('Error fetching events:', err);
        setError('Failed to load events.');
      });
  }, [filters]);

// gets locations for filter drop down
  useEffect(() => {
    axios.get('http://127.0.0.1:5000/events/filter_events')
      .then(res => setLocations(res.data))
      .catch(err => console.error('Error fetching locations', err));
  }, []);


   const handleChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  return (
    <div className="events-wrapper">
      <div className="card large-card" role="region" aria-label="Discover Events">
        <SkyBrand size={40} />
        <h1 className="brand-gradient" style={{ marginTop: 16 }}>Discover Events</h1>

        <form noValidate style={{ marginTop: 24 }}>
          <label htmlFor="keyword">Search</label>
          <input
            id="keyword"
            name="keyword"
            className="input"
            value={filters.keyword}
            onChange={handleChange}
            style={{ marginTop: 8, marginBottom: 16 }}
          />

          <label htmlFor="location">Filter by Location</label>
          <select
            id="location"
            name="location"
            className="input"
            value={filters.location}
            onChange={handleChange}
            style={{ marginTop: 8, marginBottom: 16 }}
          >
            <option value="">All Locations</option>
            {locations.map((loc, index) => (
              <option key={index} value={loc.city}>{loc.city}</option>
            ))}
          </select>

          <label htmlFor="date">Filter by Date</label>
          <input
            id="date"
            name="date"
            type="date"
            className="input"
            value={filters.date}
            onChange={handleChange}
            style={{ marginTop: 8, marginBottom: 16 }}
          />
        </form>

        {error && <div className="error" role="alert">{error}</div>}

        <div className="event-list" style={{ marginTop: 24 }}>
          {events.length > 0 ? (
            events.map((event, index) => (
              <EventCard key={event.ID ? `${event.ID}-${index}` :  `event-${index}`}
              event={event} />
            ))
          ) : (
            <p>No events found.</p>
          )}
        </div>
      </div>
    </div>
  );
}
