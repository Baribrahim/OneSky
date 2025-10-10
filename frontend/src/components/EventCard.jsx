import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import React, { useEffect, useState } from "react";
import {api, toResult} from '../lib/apiClient.js';

function EventCard() {
  const [events, setEvents] = useState([]);

const fetchEvents = async () => {
  try {
    const { data, error } = await toResult(api.get("/events/api"));
    
    //Currently when not authenticated data is null
    if (error || !Array.isArray(data)) {
      console.warn("Not authenticated", data);
      setEvents([]); 
      return;
    }
    setEvents(data);
  } catch (error) {
    console.error("Error fetching events:", error);
    setEvents([]);
  }
};

  useEffect(() => {
    fetchEvents();
  }, []);
 
  //Debugging     
  useEffect(() => {
    console.log("Updated events:", events);
    console.log(Array.isArray(events) ? "events is an array" : "events is not an array");
  }, [events]);

  return (
    <>
    {events?.map(events =>
    <div key = {events.ID} className="card">
      <div className="card-body">
        <h3 className="card-subtitle mb-2 text-muted">{events.Title}</h3>
        <p className="card-text">{events.About}</p>
        <button className="btn btn-primary">
          Sign up
        </button>
      </div>
    </div>)}
    </>
  );
}

export default EventCard;
