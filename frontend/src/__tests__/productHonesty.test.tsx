import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SampleDataBadge, PreviewBanner, TrademarkDisclaimer } from '@/components/shared/SampleDataBanner';
import { useFeatureFlagStore } from '@/lib/featureFlags';

describe('Product Honesty and Gating Components', () => {
  it('renders SampleDataBadge with expected label and testid', () => {
    render(<SampleDataBadge label="Synthetic Simulation" />);
    const badge = screen.getByTestId('sample-data-badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent('Synthetic Simulation');
  });

  it('renders PreviewBanner with title, description, and tier badge', () => {
    render(
      <PreviewBanner
        title="Demonstration Environment"
        description="This preview uses synthetic student records for platform exploration."
        tier="Tier-3 Gated"
      />
    );

    const banner = screen.getByTestId('preview-banner');
    expect(banner).toBeInTheDocument();
    expect(screen.getByText('Demonstration Environment')).toBeInTheDocument();
    expect(screen.getByText('Tier-3 Gated')).toBeInTheDocument();
  });

  it('renders TrademarkDisclaimer with non-affiliation notice', () => {
    render(<TrademarkDisclaimer />);
    const disclaimer = screen.getByTestId('trademark-disclaimer');
    expect(disclaimer).toBeInTheDocument();
    expect(disclaimer).toHaveTextContent(/All company names, logos, and brands cited on this platform are trademarks/i);
    expect(disclaimer).toHaveTextContent(/VIREONIQ is not affiliated with, sponsored by, or endorsed by/i);
  });

  it('enforces secure feature flag tier defaults', () => {
    const { isEnabled, flags } = useFeatureFlagStore.getState();
    
    // Tier 1 public features must be enabled
    expect(flags.ats_resume_studio).toBe(true);
    expect(isEnabled('ats_resume_studio')).toBe(true);
    expect(flags.interview_studio).toBe(true);
    expect(isEnabled('interview_studio')).toBe(true);

    // Tier 3 features must be disabled by default
    expect(flags.recruiter_war_room).toBe(false);
    expect(isEnabled('recruiter_war_room')).toBe(false);

    expect(flags.developer_platform).toBe(false);
    expect(isEnabled('developer_platform')).toBe(false);

    expect(flags.parent_dashboard).toBe(false);
    expect(isEnabled('parent_dashboard')).toBe(false);
  });
});
