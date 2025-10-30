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

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* ✅ Protected routes (require login) */}
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Home />} />
              <Route path="/events" element={<Events />} />
              <Route path="/events/:id" element={<EventPage />} />
            </Route>
          </Route>

          {/* ✅ Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>
);
