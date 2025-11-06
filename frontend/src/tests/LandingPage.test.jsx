
test('renders all feature highlights', () => {
  render(<WelcomePage />);
  const features = [
    /Browse events by location, date, and tags/i,
    /Register easily for events/i,
    /Join teams or create your own/i,
    /Sign up to events with your team/i,
    /Use your dashboard to track/i,
    /Leaderboard/i,
    /Earn badges/i
  ];
  features.forEach(feature => {
    expect(screen.getByText(feature)).toBeInTheDocument();
  });
});
