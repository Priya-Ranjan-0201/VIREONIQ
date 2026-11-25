import { describe, it, expect, beforeEach } from 'vitest';
import { ALL_SUPPORTED_LANGUAGES, useCodeStore } from '@/store/codeStore';

describe('useCodeStore', () => {
  beforeEach(() => {
    localStorage.clear();
    useCodeStore.setState({
      sourceCode: '# Write your solution here\n',
      languageId: 71,
      selectedLanguageKey: 'python',
      executionResult: null,
      isExecuting: false,
      error: null,
    });
  });

  it('switches language by Judge0 ID and persists preference', () => {
    useCodeStore.getState().setLanguageId(60); // Go 1.22
    const state = useCodeStore.getState();
    expect(state.languageId).toBe(60);
    expect(state.selectedLanguageKey).toBe('go');
    expect(localStorage.getItem('vireoniq_preferred_coding_language')).toBe('go');
  });

  it('switches language by key and ignores unknown keys', () => {
    useCodeStore.getState().setSelectedLanguageKey('rust');
    expect(useCodeStore.getState().languageId).toBe(73);
    expect(useCodeStore.getState().selectedLanguageKey).toBe('rust');

    useCodeStore.getState().setSelectedLanguageKey('nonexistent-lang');
    expect(useCodeStore.getState().languageId).toBe(73);
  });

  it('lists unique language IDs and keys', () => {
    const ids = new Set(ALL_SUPPORTED_LANGUAGES.map((l) => l.id));
    const keys = new Set(ALL_SUPPORTED_LANGUAGES.map((l) => l.key));
    expect(ids.size).toBe(ALL_SUPPORTED_LANGUAGES.length);
    expect(keys.size).toBe(ALL_SUPPORTED_LANGUAGES.length);
  });
});
