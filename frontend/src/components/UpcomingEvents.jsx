import React, { useEffect, useState } from 'react'
import { api, toResult } from '../lib/apiClient.js';
import '../styles/upcomingEvents.css'
import { formatDate, formatTime } from '../utils/format.jsx'

const PAGE_SIZE = 5;

const UpcomingEvents = () => {
  const [events, setEvents] = useState([]);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchEvents = async (opts = { append: false }) => {
    setLoading(true);
    try {
      const { data, error } = await toResult(
        api.get(`/dashboard/upcoming?limit=${PAGE_SIZE}&offset=${opts.append ? offset : 0}`)
      );
      if (error) {
        console.error("API error:", error);
        setLoading(false);
        return;
      }

      const nextItems = data?.upcoming_events ?? []; 
      const nextTotal = data?.total ?? 0;

      if (opts.append) {
        setEvents(prev => [...prev, ...nextItems]);
        setOffset(prev => prev + nextItems.length);
      } else {
        setEvents(nextItems);
        setOffset(nextItems.length);
      }

      setTotal(nextTotal);
      setHasMore(Boolean(data?.has_more));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents({ append: false });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <h2>Upcoming Events</h2>

      <div className="timeline-container">
        {events?.map((event) => (
          <div key={event.ID} className="timeline-item">
            <img src={`http://127.0.0.1:5000/static/${event.Image_path}`} alt={event.Title} className="timeline-image" />
            <div className="timeline-content">
              <h3>{event.Title}</h3>
              <p>{formatDate(event.Date)}</p>
              <p>{formatTime(event.StartTime)} • {event.LocationCity}</p>
              {event.RegistrationType != 'Individual' && <p>with <em>{event.RegistrationType}</em></p>}
            </div>
          </div>
        ))}

        {events.length === 0 && !loading && (
          <p className="helper" style={{ paddingLeft: 4 }}>No upcoming events.</p>
        )}

        {hasMore && (
          <div className="timeline-show-more-container">
            <button
              className="button-sky"
              disabled={loading}
              onClick={() => fetchEvents({ append: true })}
            >
              {loading ? 'Loading…' : 'Show more'}
            </button>
          </div>
        )}

        {!hasMore && events.length > 0 && total > 0 && (
          <p className="helper timeline-summary">
            Showing all {total} upcoming events.
          </p>
        )}
      </div>
    </>
  )
}

export default UpcomingEvents
