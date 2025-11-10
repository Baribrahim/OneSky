import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import Leaderboard from "../components/Leaderboard";
import * as apiClient from "../lib/apiClient";


jest.mock("../lib/apiClient", () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
  },
  toResult: jest.fn(),
}));

const mockUsers = [
    {
    FirstName: "John",
    LastName: "Doe",
    RankScore: 85,
    Email: "john@example.com",
    },
    {
    FirstName: "Jane",
    LastName: "Smith",
    RankScore: 70,
    Email: "jane@example.com",
    },
];

describe("Leaderboard", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

    it("shows loading then renders leaderboard", async () => {
        apiClient.toResult
            .mockResolvedValueOnce({ data: { users: mockUsers }, error: null })
            .mockResolvedValueOnce({ data: { currentRank: 2 }, error: null });

        render(<Leaderboard />);

        // Loading should be visible right after initial render
        expect(screen.getByText(/loading/i)).toBeInTheDocument();

        // Then after effects complete, data appears
        expect(await screen.findByText("John Doe")).toBeInTheDocument();
    });

  it("renders error message if leaderboard fetch fails", async () => {
    apiClient.toResult
      .mockResolvedValueOnce({
        data: null,
        error: { message: "Failed to load leaderboard" },
      }) // leaderboard
      .mockResolvedValueOnce({ data: { currentRank: 1 }, error: null }); // rank

    await act(async () => {
    render(<Leaderboard />);
    });

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Failed to load leaderboard");
  });

  it("renders empty state when no users are returned", async () => {
    apiClient.toResult
      .mockResolvedValueOnce({ data: { users: [] }, error: null }) // leaderboard
      .mockResolvedValueOnce({ data: { currentRank: 3 }, error: null }); // rank

    await act(async () => {
    render(<Leaderboard />);
    });

    expect(await screen.findByText(/no users yet/i)).toBeInTheDocument();
    expect(await screen.findByText(/your rank/i)).toHaveTextContent("3");
  });

  it("renders a list of ranked users", async () => {

    apiClient.toResult
      .mockResolvedValueOnce({ data: { users: mockUsers }, error: null }) // leaderboard
      .mockResolvedValueOnce({ data: { currentRank: 2 }, error: null }); // rank

    await act(async () => {
    render(<Leaderboard />);
    });

    expect(await screen.findByText("John Doe")).toBeInTheDocument();
    expect(await screen.findByText("Jane Smith")).toBeInTheDocument();
    expect(screen.getByText("85")).toBeInTheDocument();
    expect(screen.getByText("70")).toBeInTheDocument();
    expect(screen.getByText(/your rank/i)).toHaveTextContent("2");
  });

  it("shows and hides user stats when clicked", async () => {
    const mockUsers = [
      {
        FirstName: "Alice",
        LastName: "Johnson",
        RankScore: 95,
        Email: "alice@example.com",
      },
    ];

    const mockStats = {
      stats: {
        CompletedEvents: 10,
        TotalHours: 5,
        BadgesCount: 3,
      },
    };

    apiClient.toResult
      .mockResolvedValueOnce({ data: { users: mockUsers }, error: null }) // leaderboard
      .mockResolvedValueOnce({ data: { currentRank: 1 }, error: null }) // rank
      .mockResolvedValueOnce({ data: mockStats, error: null }); // stats

    await act(async () => {
    render(<Leaderboard />);
    });

    const showStatsBtn = await screen.findByText(/show stats/i);
    fireEvent.click(showStatsBtn);

    await waitFor(() =>
      expect(apiClient.api.post).toHaveBeenCalledWith("/api/leaderboard/stats", {
        email: "alice@example.com",
      })
    );

    expect(await screen.findByText(/completed events/i)).toHaveTextContent("10");
    expect(await screen.findByText(/total hours/i)).toHaveTextContent("5");

    // Use findAllByText because "Badges" appears twice (tooltip + stat)
    const badges = await screen.findAllByText(/badges/i);
    expect(badges[1]).toHaveTextContent("3");

    // Hide stats
    fireEvent.click(screen.getByText(/hide stats/i));
    await waitFor(() =>
      expect(screen.queryByText(/completed events/i)).not.toBeInTheDocument()
    );
  });

  it("displays error if fetching stats fails", async () => {
    const mockUsers = [
      {
        FirstName: "Bob",
        LastName: "Marley",
        RankScore: 90,
        Email: "bob@example.com",
      },
    ];

    apiClient.toResult
      .mockResolvedValueOnce({ data: { users: mockUsers }, error: null }) // leaderboard
      .mockResolvedValueOnce({ data: { currentRank: 1 }, error: null }) // rank
      .mockResolvedValueOnce({
        data: null,
        error: { message: "Error fetching stats" },
      }); // stats

    await act(async () => {
    render(<Leaderboard />);
    });

    const showStatsBtn = await screen.findByText(/show stats/i);
    fireEvent.click(showStatsBtn);

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Error fetching stats");
  });
});
