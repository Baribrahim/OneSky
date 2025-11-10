import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { BrowserRouter, Routes, Route } from "react-router";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import { AuthProvider } from "./context/AuthProvider.jsx";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import Events from "./pages/Events.jsx";
import EventPage from "./pages/EventPage.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Teams from "./pages/Teams.jsx";
import CreateTeam from "./pages/CreateTeam.jsx";
import Landing from "./pages/Landing.jsx";
import { Navigate } from "react-router-dom";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/landing" replace />} />
          {/* ✅ Protected routes (require login) */}
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/home" element={<Home />} />
              <Route path="/events" element={<Events />} />
              <Route path="/events/:id" element={<EventPage />} />
              <Route path="/teams" element={<Teams />} />
              <Route path="/teams/new" element={<CreateTeam />} />
            </Route>
          </Route>

          {/* ✅ Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/landing" element={<Landing />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
