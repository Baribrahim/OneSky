import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import UpcomingEvents from "../components/UpcomingEvents";
import * as apiClient from "../lib/apiClient";
import "@testing-library/jest-dom";
import userEvent from "@testing-library/user-event";

// Mock API client
jest.mock("../lib/apiClient", () => ({
  api: { get: jest.fn() },
  toResult: jest.fn(),
}));

describe("UpcomingEvents", () => {
  const mockEventsPage1 = {
    upcoming_events: [
      { ID: 1, Title: "Event 1", Date: "2025-11-05", StartTime: "10:00:00", LocationCity: "City A", Image_path: "img1.jpg", RegistrationType: "Individual" },
      { ID: 2, Title: "Event 2", Date: "2025-11-06", StartTime: "14:00:00", LocationCity: "City B", Image_path: "img2.jpg", RegistrationType: "Team Alpha" },
    ],
    total: 4,
    has_more: true,
  };

  const mockEventsPage2 = {
    upcoming_events: [
      { ID: 3, Title: "Event 3", Date: "2025-11-07", StartTime: "12:00:00", LocationCity: "City C", Image_path: "img3.jpg", RegistrationType: "Team Beta" },
      { ID: 4, Title: "Event 4", Date: "2025-11-08", StartTime: "09:00:00", LocationCity: "City D", Image_path: "img4.jpg", RegistrationType: "Individual" },
    ],
    total: 4,
    has_more: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();

    apiClient.toResult.mockImplementation((promise) =>
      promise.then((res) => ({ data: res.data, error: null }))
    );

    // Default first page
    apiClient.api.get.mockImplementation((url) => {
      if (url.includes("offset=0")) return Promise.resolve({ data: mockEventsPage1 });
      if (url.includes("offset=2")) return Promise.resolve({ data: mockEventsPage2 });
      return Promise.resolve({ data: { upcoming_events: [], total: 0, has_more: false } });
    });
  });

  it("fetches and displays initial events", async () => {
    render(<UpcomingEvents />);
    expect(apiClient.api.get).toHaveBeenCalledWith("/dashboard/upcoming?limit=5&offset=0");

    await waitFor(() => {
      expect(screen.getByText("Event 1")).toBeInTheDocument();
      expect(screen.getByText("Team Alpha")).toBeInTheDocument();
      expect(screen.getByText("Event 2")).toBeInTheDocument();
    });

    // Check registration type rendering
    expect(screen.queryByText(/with/)).toHaveTextContent("with Team Alpha");
  });

    it("does not show 'Individual' for events", async () => {
        render(<UpcomingEvents />);

        await waitFor(() => {
            // The team name is rendered
            expect(screen.getByText(/Team Alpha/i)).toBeInTheDocument();
            // "Individual" should NOT be rendered
            expect(screen.queryByText("Individual")).not.toBeInTheDocument();
        });
    });


  it("displays 'No upcoming events' if the list is empty", async () => {
    apiClient.toResult.mockResolvedValueOnce({ data: { upcoming_events: [], total: 0, has_more: false }, error: null });
    render(<UpcomingEvents />);

    await waitFor(() => {
      expect(screen.getByText("No upcoming events.")).toBeInTheDocument();
    });
  });

  it("fetches more events when 'Show more' is clicked", async () => {
    render(<UpcomingEvents />);

    await waitFor(() => screen.getByText("Event 2"));

    const showMoreButton = screen.getByRole("button", { name: /Show more/i });
    expect(showMoreButton).toBeEnabled();

    fireEvent.click(showMoreButton);

    await waitFor(() => {
      expect(screen.getByText("Event 3")).toBeInTheDocument();
      expect(screen.getByText("Event 4")).toBeInTheDocument();
      expect(screen.getByText("Team Beta")).toBeInTheDocument();
    });

    // Check offset triggered correct API call
    expect(apiClient.api.get).toHaveBeenCalledWith("/dashboard/upcoming?limit=5&offset=2");
  });

});
