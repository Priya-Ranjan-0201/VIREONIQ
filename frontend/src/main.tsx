import React, { Component, ErrorInfo, ReactNode } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// ─────────────────────────────────────────────────────────────
// 1. Vite Dynamic Import & Preload Error Auto-Recovery
// Triggered when dev server restarts or chunk hashes update
// ─────────────────────────────────────────────────────────────
window.addEventListener('vite:preloadError', (event) => {
  console.warn('Vite module preload error detected. Auto-reloading page for fresh assets:', event);
  event.preventDefault();
  const lastReload = sessionStorage.getItem('vite_preload_reload_ts');
  const now = Date.now();
  if (!lastReload || now - parseInt(lastReload, 10) > 8000) {
    sessionStorage.setItem('vite_preload_reload_ts', now.toString());
    window.location.reload();
  }
});

// Unregister any stale development Service Workers to prevent chunk caching issues
if (import.meta.env.DEV && 'serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then((registrations) => {
    for (const registration of registrations) {
      registration.unregister().then((unregistered) => {
        if (unregistered) {
          console.info('Unregistered stale development service worker:', registration.scope);
        }
      });
    }
  });
}

// ─────────────────────────────────────────────────────────────
// 2. Resilient Error Boundary
// ─────────────────────────────────────────────────────────────
interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  isChunkError: boolean;
}

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, isChunkError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    const message = error?.message || '';
    const isChunkError =
      message.includes('Failed to fetch dynamically imported module') ||
      message.includes('Importing a module script failed') ||
      message.includes('error loading dynamically imported module') ||
      message.includes('Load chunk failed');

    return { hasError: true, error, isChunkError };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo);

    const message = error?.message || '';
    const isChunkError =
      message.includes('Failed to fetch dynamically imported module') ||
      message.includes('Importing a module script failed') ||
      message.includes('error loading dynamically imported module') ||
      message.includes('Load chunk failed');

    if (isChunkError) {
      const reloadKey = 'chunk_reload_' + window.location.pathname;
      const alreadyReloaded = sessionStorage.getItem(reloadKey);
      if (!alreadyReloaded) {
        sessionStorage.setItem(reloadKey, 'true');
        console.warn('Auto-reloading page to resolve dynamic module import error...');
        window.location.reload();
      }
    }
  }

  handleReload = () => {
    sessionStorage.clear();
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/app/dashboard';
  };

  handleHardReset = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = '/login';
  };

  render() {
    if (this.state.hasError) {
      const isChunk = this.state.isChunkError;

      return (
        <div style={{
          minHeight: '100vh',
          backgroundColor: '#0B1020',
          color: '#F3F4F6',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '2rem',
          fontFamily: 'Inter, system-ui, -apple-system, sans-serif'
        }}>
          <div style={{
            maxWidth: '540px',
            width: '100%',
            backgroundColor: '#141A2E',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            borderRadius: '1.5rem',
            padding: '2.5rem 2rem',
            textAlign: 'center',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)'
          }}>
            <div style={{
              display: 'inline-flex',
              padding: '0.75rem',
              borderRadius: '1rem',
              backgroundColor: isChunk ? 'rgba(99, 102, 241, 0.15)' : 'rgba(239, 68, 68, 0.15)',
              marginBottom: '1rem'
            }}>
              <span style={{ fontSize: '1.75rem' }}>{isChunk ? '🔄' : '⚠️'}</span>
            </div>

            <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '0.5rem', letterSpacing: '-0.025em' }}>
              {isChunk ? 'Module Update Detected' : 'Application Notice'}
            </h1>
            <p style={{ color: '#9CA3AF', marginBottom: '1.5rem', fontSize: '0.875rem', lineHeight: 1.5 }}>
              {isChunk
                ? 'A page component was recently updated. A quick refresh will load the latest module without losing your login session.'
                : 'An unexpected interface error occurred while rendering this view.'}
            </p>

            <pre style={{
              backgroundColor: 'rgba(0,0,0,0.5)',
              border: '1px solid rgba(255,255,255,0.06)',
              padding: '0.875rem',
              borderRadius: '0.75rem',
              fontSize: '0.75rem',
              color: isChunk ? '#818CF8' : '#F87171',
              textAlign: 'left',
              overflowX: 'auto',
              marginBottom: '1.5rem',
              fontFamily: 'monospace',
              maxHeight: '120px'
            }}>
              {this.state.error?.message || 'Unknown Error'}
            </pre>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <button
                onClick={this.handleReload}
                style={{
                  backgroundColor: '#4F46E5',
                  color: '#FFFFFF',
                  border: 'none',
                  padding: '0.875rem 1.5rem',
                  borderRadius: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  boxShadow: '0 4px 14px rgba(79, 70, 229, 0.4)',
                  transition: 'all 0.2s'
                }}
              >
                Reload & Continue
              </button>

              <button
                onClick={this.handleGoHome}
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  color: '#E5E7EB',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  padding: '0.75rem 1.5rem',
                  borderRadius: '0.75rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  fontSize: '0.875rem'
                }}
              >
                Return to Dashboard
              </button>
            </div>

            <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
              <button
                onClick={this.handleHardReset}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#6B7280',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                  textDecoration: 'underline'
                }}
              >
                Reset Session & Return to Login
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
