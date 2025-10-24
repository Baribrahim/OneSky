import React from "react";
import { useAuth } from "../context/AuthProvider";
import ImpactContainer from "../components/ImpactComponent/ImpactContainer";
import UpcomingEvents from "../components/UpcomingEvents";
import BadgesDisplay from "../components/BadgesDisplay";

export default function Home() {
  const { user, logout } = useAuth();

  return (
    <>
      {/* Impact section stays full-width and handles its own layout */}
      <ImpactContainer />
      
      {/* Main content area with two columns */}
      <div className="home-content">
        <div className="home-left">
          <UpcomingEvents />
        </div>
        <div className="home-right">
          <BadgesDisplay />
        </div>
      </div>
    </>
  );
}
