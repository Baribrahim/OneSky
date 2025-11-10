import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import Profile from "../pages/Profile";
import * as apiClient from "../lib/apiClient";

jest.mock("../lib/apiClient", () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
  },
  toResult: jest.fn(),
}));

const mockUser = {
  info: {
    FirstName: "Alice",
    LastName: "Johnson",
    Email: "alice@example.com",
    DateJoined: "2023-04-10T00:00:00.000Z",
    ProfileImgURL: "/uploads/alice.jpg",
  },
};

describe("Profile Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // Renders all profile info
  it("renders profile information correctly", async () => {
    apiClient.toResult.mockResolvedValueOnce({ data: mockUser, error: null });

    render(<Profile />);
    await screen.findByText("Alice");

    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Johnson")).toBeInTheDocument();
    expect(screen.getByText("alice@example.com")).toBeInTheDocument();
    expect(screen.getByText("April 2023")).toBeInTheDocument();
  });


  // Uploads profile image successfully
  it("uploads profile image successfully", async () => {
    apiClient.toResult.mockResolvedValueOnce({ data: mockUser, error: null });
    render(<Profile />);
    await screen.findByText("Alice");

    const fileInput = screen.getByLabelText(/upload profile picture/i);
    const file = new File(["test"], "avatar.png", { type: "image/png" });

    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(apiClient.api.post).toHaveBeenCalledWith(
        expect.stringContaining("/api/profile/update-image"),
        expect.any(FormData),
        expect.any(Object)
      );
    });
  });
  
    // Shows validation error for weak new password
   it("shows validation error for weak new password", async () => {
    apiClient.toResult.mockResolvedValueOnce({ data: mockUser, error: null });
    render(<Profile />);
    await screen.findByText("Alice");

    const newPasswordInput = screen.getByLabelText(/^new password$/i);
    fireEvent.change(newPasswordInput, { target: { value: "weak" } });

    expect(
      screen.getByText(/Password must be at least 8 characters and include an uppercase letter, a number, and a special character./i)
    ).toBeInTheDocument();
  });

    // Shows error if confirm password doesn’t match
  it("shows error if confirm password does not match", async () => {
    apiClient.toResult.mockResolvedValueOnce({ data: mockUser, error: null });
    render(<Profile />);
    await screen.findByText("Alice");

    const newPasswordInput = screen.getByLabelText(/^new password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);

    fireEvent.change(newPasswordInput, { target: { value: "StrongPass1!" } });
    fireEvent.change(confirmPasswordInput, { target: { value: "Mismatch1!" } });

    expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
  });

  // Successfully updates password
  it("updates password successfully", async () => {
    apiClient.toResult
      .mockResolvedValueOnce({ data: mockUser, error: null }) // initial fetch
      .mockResolvedValueOnce({ data: {}, error: null }); // password update success

    render(<Profile />);
    await screen.findByText("Alice");

    fireEvent.change(screen.getByLabelText(/old password/i), {
      target: { value: "OldPass1!" },
    });
    fireEvent.change(screen.getByLabelText(/^new password$/i), {
      target: { value: "NewPass1!" },
    });
    fireEvent.change(screen.getByLabelText(/confirm new password/i), {
      target: { value: "NewPass1!" },
    });

    fireEvent.click(screen.getByRole("button", { name: /update password/i }));

    expect(await screen.findByText(/password updated successfully/i)).toBeInTheDocument();
  });

  
});
