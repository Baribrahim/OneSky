import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import TeamCard from "../components/TeamCard";
import * as apiClient from "../lib/apiClient";

// Mock the API client
jest.mock("../lib/apiClient", () => ({
  api: {
    post: jest.fn(),
  },
  toResult: jest.fn(),
}));

describe("TeamCard", () => {
  const mockTeam = {
    id: 1,
    name: "Engineering",
    description: "Frontend team",
    department: "Tech",
    join_code: "ABC123",
  };

  beforeEach(() => {
    jest.clearAllMocks();
    apiClient.api.post.mockResolvedValue({ data: { success: true } });
    apiClient.toResult.mockImplementation((promise) =>
      promise.then((res) => ({ data: res.data, error: null }))
    );
  });

  it("renders team info", () => {
    render(<TeamCard team={mockTeam} />);
    expect(screen.getByText(/engineering/i)).toBeInTheDocument();
    expect(screen.getByText(/frontend team/i)).toBeInTheDocument();
    expect(screen.getByText(/Dept: Tech/i)).toBeInTheDocument();
  });

  it("renders buttons", () => {
    render(<TeamCard team={mockTeam} />);
    expect(
      screen.getByRole("button", { name: /request to join/i })
    ).toBeInTheDocument();
  });

  it("shows error if join is attempted with empty code", async () => {
    render(<TeamCard team={mockTeam} />);
    fireEvent.click(screen.getByRole("button", { name: /request to join/i }));
    fireEvent.click(screen.getByRole("button", { name: /submit/i }));

  expect(await screen.findByText("Join code is required.")).toBeInTheDocument();

  });

  it("calls API when join code is entered", async () => {
    render(<TeamCard team={mockTeam} />);
    fireEvent.click(screen.getByRole("button", { name: /request to join/i }));
    fireEvent.change(screen.getByPlaceholderText("Code"), {
      target: { value: "ABC123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    await waitFor(() =>
      expect(apiClient.api.post).toHaveBeenCalledWith("/api/teams/join", {
        team_id: mockTeam.id,
        join_code: "ABC123",
      })
    );
  });

  it("simulates a failed join attempt", async () => {
    apiClient.api.post.mockResolvedValue({
      data: { success: false, message: "Invalid code" },
    });
    apiClient.toResult.mockImplementation((promise) =>
      promise.then((res) => ({
        data: null,
        error: { message: res.data.message },
      }))
    );

    render(<TeamCard team={mockTeam} />);
    fireEvent.click(screen.getByRole("button", { name: /request to join/i }));
    fireEvent.change(screen.getByPlaceholderText("Code"), {
      target: { value: "WRONGCODE" },
    });
    fireEvent.click(screen.getByRole("button", { name: /submit/i }));

    expect(await screen.findByText("Invalid code")).toBeInTheDocument();

  });

  it("does not render request to join button if already in team", () => {
    render(<TeamCard team={mockTeam} isMember={true} />);
    const joinBtn = screen.queryByRole("button", {
      name: /request to join/i,
    });
    expect(joinBtn).not.toBeInTheDocument();
  });

  it("does not render leave button if not team owner", () => {
    render(<TeamCard team={mockTeam} isOwner={false} />);
    const vmbtn = screen.queryByRole("button", { name: /leave/i });
    expect(vmbtn).not.toBeInTheDocument();
  });

  it("renders delete if team owner", () => {
    render(<TeamCard team={mockTeam} isOwner={true} />);
    expect(
      screen.getByRole("button", { name: /delete/i })
    ).toBeInTheDocument();
  });

  it("renders join code only if showJoinCode is true", () => {
    render(<TeamCard team={mockTeam} showJoinCode={true} />);
    expect(screen.getByText(/Join Code: ABC123/i)).toBeInTheDocument();
  });

  it("does not render join code by default", () => {
    render(<TeamCard team={mockTeam} />);
    expect(screen.queryByText(/Join Code: ABC123/i)).not.toBeInTheDocument();
  });
});
