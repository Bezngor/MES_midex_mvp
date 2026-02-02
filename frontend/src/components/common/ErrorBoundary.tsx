/**
 * Error Boundary: при ошибке в дочернем дереве показывает fallback вместо белого экрана.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg max-w-2xl mx-auto mt-8">
          <h2 className="text-lg font-semibold text-red-800">Что-то пошло не так</h2>
          <p className="mt-2 text-sm text-red-700">{this.state.error.message}</p>
          <p className="mt-2 text-xs text-gray-600">Проверьте консоль браузера (F12) для подробностей.</p>
          <button
            type="button"
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
          >
            Закрыть
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
