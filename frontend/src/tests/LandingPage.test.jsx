import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import WelcomePage from '../pages/Landing';

// ✅ Mock child components to avoid unrelated errors
jest.mock('../components/Header.jsx', () => () => <div>Header</div>);
jest.mock('../components/Footer.jsx', () => () => <div>Footer</div>);
jest.mock('../components/Testimonials.jsx', () => () => <div>Testimonials</div>);
jest.mock('../components/TeamCard.jsx', () => () => <div>TeamCard</div>);

// ✅ Mock all non-JS assets used in the component
jest.mock('../assets/Welcome (1).mp4', () => 'video-mock');
jest.mock('../assets/welcomePage/search.png', () => 'image-mock');
jest.mock('../assets/welcomePage/events.png', () => 'image-mock');
jest.mock('../assets/welcomePage/team.png', () => 'image-mock');
jest.mock('../assets/welcomePage/chatbot.jpg', () => 'image-mock');
jest.mock('../assets/welcomePage/leaderboard.png', () => 'image-mock');
jest.mock('../assets/OneSky-logo.png', () => 'image-mock');

describe('WelcomePage', () => {
  test('renders all feature titles (headings)', () => {
    render(
      <MemoryRouter>
        <WelcomePage />
      </MemoryRouter>
    );

    const featureTitles = [
      /Search and Filter Events/i,
      /Join Events/i,
      /Create and Join Teams/i,
      /Leaderboard and Badges/i,
      /Interactive Chatbot/i,
    ];

    featureTitles.forEach(title => {
      expect(screen.getByRole('heading', { name: title })).toBeInTheDocument();
    });
  });

  test('renders main heading and both CTAs', () => {
    render(
      <MemoryRouter>
        <WelcomePage />
      </MemoryRouter>
    );

    // Main heading
    expect(screen.getByText(/Make an Impact with OneSky/i)).toBeInTheDocument();

    // Two "Sign Up Today" links (hero + footer)
    const ctas = screen.getAllByText(/Sign Up Today/i);
    expect(ctas).toHaveLength(2);
  });

});