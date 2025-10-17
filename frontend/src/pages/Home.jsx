import React from "react";
import { useAuth } from "../context/AuthProvider";
import ImpactContainer from "../components/ImpactComponent/ImpactContainer";

export default function Home() {
  const { user, logout } = useAuth();

  return (
    <>
      {/* Impact section stays full-width and handles its own layout */}
      <ImpactContainer />
    </>
  );
}
