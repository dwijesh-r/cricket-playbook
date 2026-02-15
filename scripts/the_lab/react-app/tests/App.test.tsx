import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../src/App';

describe('App', () => {
  it('renders the home page with the Cricket Playbook title', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    );

    expect(screen.getByText('Playbook')).toBeInTheDocument();
  });

  it('renders the comparison page when navigating to /comparison', () => {
    render(
      <MemoryRouter initialEntries={['/comparison']}>
        <App />
      </MemoryRouter>,
    );

    expect(screen.getByText('Player Comparison Tool')).toBeInTheDocument();
  });

  it('renders the win probability page when navigating to /win-probability', () => {
    render(
      <MemoryRouter initialEntries={['/win-probability']}>
        <App />
      </MemoryRouter>,
    );

    expect(screen.getByText('Win Probability Curves')).toBeInTheDocument();
  });

  it('shows navigation links in the layout', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Comparison')).toBeInTheDocument();
    expect(screen.getByText('Win Probability')).toBeInTheDocument();
  });

  it('renders the footer with version info', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    );

    expect(screen.getByText(/Cricket Playbook v5\.0\.0/)).toBeInTheDocument();
  });
});
