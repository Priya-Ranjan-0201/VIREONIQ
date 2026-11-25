import { describe, it, expect, beforeEach } from 'vitest';
import { I18nManager } from '../lib/i18n';

describe('I18nManager Internationalization Suite', () => {
  let i18n: I18nManager;

  beforeEach(() => {
    i18n = new I18nManager();
  });

  it('translates English strings by default', () => {
    expect(i18n.getLocale()).toBe('en');
    expect(i18n.t('platform.title')).toBe('VIREONIQ — Career Intelligence');
    expect(i18n.t('rag.abstain')).toContain('enough verified evidence');
  });

  it('switches to Hindi and provides accurate localized strings', () => {
    i18n.setLocale('hi');
    expect(i18n.getLocale()).toBe('hi');
    expect(i18n.t('platform.title')).toBe('विरेओनिक — करियर इंटेलिजेंस');
    expect(i18n.t('career.readiness')).toBe('करियर तैयारी सूचकांक');
    expect(i18n.t('rag.abstain')).toContain('सत्यापित प्रमाण');
  });

  it('falls back to English when a key is missing in the target locale', () => {
    i18n.setLocale('hi');
    // If a non-existent key is queried, returns key or fallback
    expect(i18n.t('non.existent.key', 'Fallback Text')).toBe('Fallback Text');
  });

  it('formats numbers according to the active locale', () => {
    i18n.setLocale('en');
    const formattedEn = i18n.formatNumber(150000);
    expect(formattedEn).toBe('150,000');

    i18n.setLocale('hi');
    const formattedHi = i18n.formatNumber(150000);
    // Hindi formatting uses Indian numbering system (1,50,000)
    expect(formattedHi).toBe('1,50,000');
  });
});
