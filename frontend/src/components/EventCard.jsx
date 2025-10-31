import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import React, { useEffect, useState } from "react";
import {api, toResult} from '../lib/apiClient.js';
import { useAuth } from '../context/AuthProvider'
import { formatDate, formatTime, timeUnicode } from '../utils/format.jsx';


// I have changed eventCard so that it represents an individual event and no longer fetches all events. The event card now only handles signup/unregister. This means that the events page(parent) handles the filtering and fetching, and eventcard(child) handles the display and interaction. 

function EventCard({ event }) {
  const { user } = useAuth(); //gets current user info
  const [isSignedUp, setIsSignedUp] = useState(false); //tracks signup for individual event 

  // Fetch signup status for this specific event
  const fetchSignupStatus = async () => {
    const { data, error } = await toResult(api.get("/api/events/signup-status"));
    if (!error && Array.isArray(data)) {
      setIsSignedUp(data.includes(event.ID)); //is this event in the users signup list
    }
  };

  useEffect(() => {
    fetchSignupStatus();
  }, []);

  const handleSignup = async () => {
    const { data, error } = await toResult(api.post("/api/events/signup", { event_id: event.ID }));
    if (!error) {
      setIsSignedUp(true);
    } else {
      console.error("Signup failed:", error.message);
    }
  };

  const handleUnregister = async () => {
    const { data, error } = await toResult(api.post("/api/events/unregister", { event_id: event.ID }));
    if (!error) {
      setIsSignedUp(false);
    } else {
      console.error("Unregister failed:", error.message);
    }
  };

  return (
    <div className="card event-card">
      {/* When we depoloy this it update the URL to match backend domain/ api base url */}
      <img className='event-image' src={`http://127.0.0.1:5000/static/${event.Image_path}`}
          alt={event.Title}
        />
      <div className="card-body">
        <h3 className="card-subtitle mb-2 text-muted">{event.Title}</h3>
        <p className="card-text">{event.About}</p>
        <div className="event-info">
          <div className='event-location'>
            <span role="img" aria-label="location">{'\u{1F4CD}'}</span>
            {event.Address}, {event.LocationCity}, {event.LocationPostcode}
          </div>

          <p className="card-text">{'\u{1F4C5}'} {formatDate(event.Date)}</p>
          <p className="card-text">
            {timeUnicode(event.StartTime)} {formatTime(event.StartTime)} - {formatTime(event.EndTime)}
          </p>
          <p className="card-text">{'\u{1F465}'} {event.Capacity}</p>
        </div>

        {isSignedUp ? (
          <button className="button inverse" onClick={handleUnregister}>
            Unregister
          </button>
        ) : (
          <button className="button" onClick={handleSignup}>
            Register
          </button>
        )}
      </div>
    </div>
  );
}

export default EventCard;

// Schivanee's event card origional code: 

// function EventCard() {
//   const [events, setEvents] = useState([]);
//   const {user} = useAuth();
//   const [signupEvents, setSignupEvents] = useState([]);

//   const fetchEvents = async () => {
//     try {
//       const { data, error } = await toResult(api.get("/api/events"));
      
//       if (error || !Array.isArray(data)) {
//         console.warn("Not authenticated", data);
//         return;
//       }
//       setEvents(data);
//     } catch (error) {
//       console.error("Error fetching events:", error);
//     }
//   };

//   const fetchStatuses = async () => {
//     const { data, error } = await toResult(api.get(`/api/events/signup-status`));
//     setSignupEvents(data);
//     console.log("Fetched signup statuses:", signupEvents);
//   };

//   useEffect(() => {
//     fetchEvents();
//   }, []);

//   useEffect(() => {
//     if (events.length > 0) {
//       fetchStatuses()
//     }
//   }, [events])

//   // //Debugging     
//   // useEffect(() => {
//   //   console.log("Updated events:", events);
//   //   console.log(Array.isArray(events) ? "events is an array" : "events is not an array");
//   // }, [events]);

//   const handleSignup = async (event_id) => {
//     try {
//       const { data, error } = await toResult(api.post("api/events/signup", { event_id}));
//       if (error) {
//         console.error("Signup failed:", error.message);
//       } 
//       else {
//         setSignupEvents(prev => ([...prev, event_id])); 
//       }
//     } 
//     catch (err) {
//       console.error("Unexpected error during signup:", err);
//     }
//   };

//   const handleUnregister = async (event_id) => {
//     const { data, error } = await toResult(api.post("api/events/unregister", {event_id}));
//     if (error) {
//       console.error("Unregister failed:", error.message);
//     } 
//     else {
//       setSignupEvents(prev => prev.filter(id => id !== event_id)); 
//     }
    
//   }

//   return (
//     <>
//     <div className="cards-container">
//     {events?.map(events =>
//     <div key = {events.ID} className="card">
//       <div className="card-body">
//         <h3 className="card-subtitle mb-2 text-muted">{events.Title}</h3>
//         <p className="card-text">{events.About}</p>
//         <div className="event-info">
//         <p className="card-text">{'\u{1F4CD}'} {events.LocationCity}</p> 
//         <p className="card-text">{'\u{1F4C5}'} {formatDate(events.Date)}</p>
//         <p className="card-text">{timeUnicode(events.StartTime)} {formatTime(events.StartTime)} - {formatTime(events.EndTime)}</p>
//         <p className="card-text">{'\u{1F465}'} {events.Capacity}</p>
//         </div> 
//         {signupEvents.includes(events.ID)? (
//                       <button className="button inverse" onClick={() => handleUnregister(events.ID)}>
//                         Unregister
//                       </button>
//                     ) : (
//                       <button className="button" onClick={() => handleSignup(events.ID)}>
//                         Register
//                       </button>
//         )}
//       </div>
//     </div>
//     )}
//     </div>
//     </>
//   );
// }

// export default EventCard;