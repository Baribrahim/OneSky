import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import EventHeader from '../components/EventComponents/EventHeader';
import EventInfoCards from '../components/EventComponents/EventInfoCards';
import EventDescription from '../components/EventComponents/EventDescription';
import EventActivities from '../components/EventComponents/EventActivities';
import EventRequirements from '../components/EventComponents/EventRequirements';
import EventMap from '../components/EventComponents/EventMap';
import EventActions from '../components/EventComponents/EventActions';

function EventPage(){
    const { id } = useParams();
    const [event, setEvent] = useState(null); //State to store event data
    const [loading, setLoading] = useState(true); // Loading state
    const [error, setError] = useState(null); // Error state

    useEffect(() => {
        async function fetchEvent() {
            try {
                const response = await fetch(`http://localhost:5000/api/events/events/${id}`);
                if (!response.ok) {
                    throw new Error('Event not found');
                }
                const data = await response.json();
                setEvent(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }

        fetchEvent ();
    }, [id]);

    if (loading) return <p>Loading event...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div className="events-wrapper">
            <div className="page-container">
                <EventHeader
                title={event.Title}
                causeName={event.CauseName}
                tags={event.TagName}
                />

                <EventInfoCards
                date={event.Date}
                startTime={event.StartTime}
                endTime={event.EndTime}
                address={event.Address}
                location={event.LocationCity}
                locationPostCode={event.LocationPostcode}
                capacity={event.Capacity}
                causeName={event.CauseName}
                />

                <EventActions event={event} />

                <EventDescription about={event.About} />

                <div className="event-details-container">
                <div className="left-column">
                    <EventActivities activities={event.Activities} />
                    <EventRequirements
                    requirementsBring={event.RequirementsBring}
                    requirementsProvided={event.RequirementsProvided}
                    />
                </div>
                <div className="right-column">
                    <EventMap latitude={event.Latitude} longitude={event.Longitude} />
                </div>
                </div>
            </div>
        </div>
    );
}

export default EventPage;