import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, describe, it, beforeEach, afterEach, expect } from "vitest";
import EventTeamsPopup from "../components/EventTeamsPopup";
import * as apiClient from "../lib/apiClient";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

// Mock the Popup library 
vi.mock("reactjs-popup", () => ({
  __esModule: true,
  default: ({ trigger, children, onOpen }) => (
    <div>
      <div onClick={onOpen} data-testid="trigger">{trigger}</div>
      <div data-testid="popup">{typeof children === "function" ? children(() => {}) : children}</div>
    </div>
  ),
}));

// Mock the API client
vi.mock("../lib/apiClient");

describe("EventTeamsPopup", () => {
  const mockTeams = [
    { ID: 1, Name: "Team Alpha", isRegistered: 1 },
    { ID: 2, Name: "Team Beta", isRegistered: 0 },
    { ID: 3, Name: "Team Gamma", isRegistered: 0 },
  ];

  beforeEach(() => {
    // Default: successful GET and POST
    apiClient.api.get = vi.fn(() => Promise.resolve({ data: { teams: mockTeams } }));
    apiClient.api.post = vi.fn(() => Promise.resolve({ data: { message: "ok" } }));

    apiClient.toResult.mockImplementation((promise) =>
      promise.then((res) => ({ data: res.data, error: null }))
    );
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ---------------------------------------------------------
  // FETCH TEAMS
  // ---------------------------------------------------------
  it("fetches and displays teams when opened", async () => {
    render(<EventTeamsPopup eventID={5} />);

    // Open popup (simulate trigger click)
    fireEvent.click(screen.getByTestId("trigger"));

    expect(apiClient.api.get).toHaveBeenCalledWith("/api/events/5/available-teams");

    // Wait for teams to render
    await waitFor(() => {
      expect(screen.getByText("Team Alpha")).toBeInTheDocument();
      expect(screen.getByText("Team Beta")).toBeInTheDocument();
    });
  });

  it("shows loading state while teams are fetched", async () => {
    let resolveFn;
    apiClient.api.get = vi.fn(() => new Promise((r) => (resolveFn = r)));

    render(<EventTeamsPopup eventID={1} />);
    fireEvent.click(screen.getByTestId("trigger"));

    expect(screen.getByText(/loading teams/i)).toBeInTheDocument();

    // Resolve the pending promise
    resolveFn({ data: { teams: mockTeams } });
    await waitFor(() => expect(screen.queryByText(/loading teams/i)).not.toBeInTheDocument());
  });

  it("shows error if fetching teams fails", async () => {
    apiClient.toResult.mockResolvedValueOnce({ data: null, error: { message: "Network error" } });

    render(<EventTeamsPopup eventID={1} />);
    fireEvent.click(screen.getByTestId("trigger"));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Network error");
    });
  });

  it("shows message if no teams are available", async () => {
    apiClient.toResult.mockResolvedValueOnce({ data: { teams: [] }, error: null });

    render(<EventTeamsPopup eventID={99} />);
    fireEvent.click(screen.getByTestId("trigger"));

    await waitFor(() => {
      expect(screen.getByText(/no teams available/i)).toBeInTheDocument();
    });
  });

  it("displays 'Registered' for teams that are registered and prevents click", async () => {
    render(<EventTeamsPopup eventID={5} />);
    fireEvent.click(screen.getByTestId("trigger"));

    await waitFor(() => screen.getByText("Team Alpha"));

    // Check registered label
    expect(screen.getByText("Registered")).toBeInTheDocument();

    // Click registered team should not select
    const registeredTeam = screen.getByText("Team Alpha").closest("li");
    await userEvent.click(registeredTeam);
    expect(registeredTeam).not.toHaveClass("selected");

    // Click unregistered team should select
    const unregisteredTeam = screen.getByText("Team Beta").closest("li");
    await userEvent.click(unregisteredTeam);
    expect(unregisteredTeam).toHaveClass("selected");
  });

  // ---------------------------------------------------------
  // TEAM SELECTION & SUBMISSION
  // ---------------------------------------------------------
  it("stores selected team IDs when user selects them", async () => {
    render(<EventTeamsPopup eventID={5} />);
    fireEvent.click(screen.getByTestId("trigger"));

    await waitFor(() => screen.getByText("Team Alpha"));

    const teamItems = screen.getAllByRole('listitem');
    await userEvent.click(teamItems[1]);
    await userEvent.click(teamItems[2]);

    // Simulate submit button
    const submitBtn = screen.getByRole("button", { name: /submit/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(apiClient.api.post).toHaveBeenCalledWith("/api/events/signup-team", {
        event_id: 5,
        team_id: 2,
      });
      expect(apiClient.api.post).toHaveBeenCalledWith("/api/events/signup-team", {
        event_id: 5,
        team_id: 3,
      });
    });
  });
});
