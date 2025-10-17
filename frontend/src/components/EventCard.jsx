import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import React, { useEffect, useState } from "react";

function EventCard() {
      const [events, setEvents] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/events")
      .then((res) => res.json())
      .then((data) => setEvents(data))
      .catch((err) => console.error("Error fetching events:", err));
  }, []);

  return (
    <Card style={{ width: '25rem', backgroundColor: '#365b81ff'}}>
      <Card.Body>
        <Card.Title>{events}</Card.Title>
        <Card.Subtitle className="mb-2 text-muted">{events}</Card.Subtitle>
        <Card.Text>
          Some quick example text to build on the card title and make up the
          bulk of the card's content.
        </Card.Text>
        <Button className="me-2"> Card Link</Button>
        <Button className="me-2">Another Link</Button>
      </Card.Body>
    </Card>

  );
}

export default EventCard;
