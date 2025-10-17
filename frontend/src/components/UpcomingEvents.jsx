import React from 'react'
import { useEffect, useState } from 'react'
import {api, toResult} from '../lib/apiClient.js';
import '../styles/theme.css'
import {formatDate, formatTime} from '../utils/format.jsx'

const UpcomingEvents = () => {

    const [events, setEvents] = useState([]);

    const fetchEvents = async () => {
      try {
        const { data, error } = await toResult(api.get("/dashboard/upcoming"));
        
        if (error) {
          console.error("API error:", error);
          return;
        }

        setEvents(data);
      } 
      catch (err) {
        console.error(err);
      }
    }

    useEffect(() => {
      fetchEvents();
    }, []);
    
    return (
    <>
    <h2>Upcoming Events</h2>
    <div className="timeline-container">
      {events.upcoming_events?.map((event) => (
        <div key={event.ID} className="timeline-item">
          <div className="timeline-dot"></div>
          <div className="timeline-content">
            <h3>{event.Title}</h3>
            <p>{formatDate(event.Date)}</p>
            <p>{formatTime(event.StartTime)} • {event.LocationCity}</p>
          </div>
        </div>
      ))}
    </div>
    </>

  )
}

export default UpcomingEvents