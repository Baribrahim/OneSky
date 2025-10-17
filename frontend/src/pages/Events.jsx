
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

}
