import React from "react";
import { Navigate, Outlet, useLocation } from "react-router";
import { useAuth } from "../context/AuthProvider";

export default function ProtectedRoute() {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) return null; // optional spinner later
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location }} />;
  return <Outlet />;
}
