import React from "react";
import { useAuth } from "../context/AuthProvider";
import ImpactContainer from "../components/ImpactComponent/ImpactContainer";
import UpcomingEvents from "../components/UpcomingEvents";
import TeamCard from "../components/TeamCard";

export default function Home() {
  const { user, logout } = useAuth();

  return (
    <>
      {/* Impact section stays full-width and handles its own layout */}
      <ImpactContainer />
      <UpcomingEvents />
      <TeamCard />
    </>
  );
}
