import React from "react";
import { Outlet } from "react-router";
import Header from "./Header";
import Footer from "./Footer";

/**
 * Layout
 * ------------------------------------------------------------------
 * Global shell that wraps all protected pages with a Header and Footer.
 * The <Outlet /> renders the active child route's page (e.g., Home, Events).
 */
export default function Layout() {
  return (
    <div className="app-shell">
      <Header />

      {/* Main content area for pages */}
      <main className="app-content">
        <Outlet />
      </main>

      <Footer />

      {/* Minimal layout styling (uses your theme tokens) */}
      <style>{`
        .app-shell {
          display: flex;
          min-height: 100vh;
          flex-direction: column;
          background: var(--color-bg);
          color: var(--color-text);
        }
        .app-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          padding: var(--space-6) var(--space-8);
        }
      `}</style>
    </div>
  );
}
