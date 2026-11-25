/**
 * Lightweight Internationalization (i18n) Utility.
 * Supports English (en) and Hindi (hi) strings for career readiness,
 * ATS scoring, and uncertainty/abstention UI banners.
 */

export type SupportedLocale = 'en' | 'hi';

export const translations: Record<SupportedLocale, Record<string, string>> = {
  en: {
    'platform.title': 'VIREONIQ — Career Intelligence',
    'auth.login': 'Log In',
    'auth.register': 'Create Account',
    'career.readiness': 'Career Readiness Index',
    'career.bottlenecks': 'Skill Bottlenecks',
    'rag.abstain': 'I do not have enough verified evidence to answer this with confidence.',
    'rag.citations': 'Cited Evidence Spans',
    'ats.score': 'ATS Compatibility Score',
    'common.loading': 'Loading...',
    'common.error': 'An unexpected error occurred. Please try again.',
  },
  hi: {
    'platform.title': 'विरेओनिक — करियर इंटेलिजेंस',
    'auth.login': 'लॉग इन करें',
    'auth.register': 'खाता बनाएं',
    'career.readiness': 'करियर तैयारी सूचकांक',
    'career.bottlenecks': 'कौशल बाधाएं',
    'rag.abstain': 'विश्वसनीय मार्गदर्शन प्रदान करने के लिए पर्याप्त सत्यापित प्रमाण उपलब्ध नहीं हैं।',
    'rag.citations': 'उद्धृत प्रमाण',
    'ats.score': 'एटीएस संगतता स्कोर',
    'common.loading': 'लोड हो रहा है...',
    'common.error': 'एक अप्रत्याशित त्रुटि हुई। कृपया पुनः प्रयास करें।',
  },
};

export class I18nManager {
  private currentLocale: SupportedLocale = 'en';

  setLocale(locale: SupportedLocale): void {
    if (locale in translations) {
      this.currentLocale = locale;
    }
  }

  getLocale(): SupportedLocale {
    return this.currentLocale;
  }

  t(key: string, fallback?: string): string {
    const localeDict = translations[this.currentLocale];
    if (localeDict && key in localeDict) {
      return localeDict[key];
    }
    // Fallback to English
    if (translations.en && key in translations.en) {
      return translations.en[key];
    }
    return fallback || key;
  }

  formatDate(date: Date): string {
    return new Intl.DateTimeFormat(this.currentLocale === 'hi' ? 'hi-IN' : 'en-US', {
      dateStyle: 'medium',
    }).format(date);
  }

  formatNumber(val: number): string {
    return new Intl.NumberFormat(this.currentLocale === 'hi' ? 'hi-IN' : 'en-US').format(val);
  }
}

export const i18n = new I18nManager();
