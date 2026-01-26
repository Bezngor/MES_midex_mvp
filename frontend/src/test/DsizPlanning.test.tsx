/**
 * Тесты для DsizPlanningPage
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { DsizPlanningPage } from '../pages/DsizPlanningPage';
import { useDsizPlanning } from '../hooks/useDsizPlanning';

// Mock hooks
vi.mock('../hooks/useDsizPlanning');

describe('DsizPlanningPage', () => {
  const mockRunPlanning = vi.fn();
  const mockClearError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    (useDsizPlanning as ReturnType<typeof vi.fn>).mockReturnValue({
      planningData: null,
      loading: false,
      error: null,
      runPlanning: mockRunPlanning,
      clearError: mockClearError,
    });
  });

  it('должен отображать заголовок "Планирование реакторов"', () => {
    render(
      <BrowserRouter>
        <DsizPlanningPage />
      </BrowserRouter>
    );

    expect(screen.getByText('Планирование реакторов')).toBeInTheDocument();
  });

  it('должен отображать форму параметров планирования', () => {
    render(
      <BrowserRouter>
        <DsizPlanningPage />
      </BrowserRouter>
    );

    expect(screen.getByText('Параметры планирования')).toBeInTheDocument();
    expect(screen.getByLabelText(/Дата начала планирования/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Горизонт планирования/i)).toBeInTheDocument();
    // input type="number" имеет роль "spinbutton", не "textbox"
    expect(screen.getByRole('spinbutton', { name: /Горизонт планирования/i })).toBeInTheDocument();
  });

  it('должен отображать кнопку "Запустить планирование"', () => {
    render(
      <BrowserRouter>
        <DsizPlanningPage />
      </BrowserRouter>
    );

    const button = screen.getByRole('button', { name: /Запустить планирование/i });
    expect(button).toBeInTheDocument();
    expect(button).not.toBeDisabled();
  });

  it('должен вызывать runPlanning при нажатии на кнопку "Запустить планирование"', async () => {
    const user = userEvent.setup();
    
    render(
      <BrowserRouter>
        <DsizPlanningPage />
      </BrowserRouter>
    );

    const button = screen.getByRole('button', { name: /Запустить планирование/i });
    await user.click(button);

    await waitFor(() => {
      expect(mockRunPlanning).toHaveBeenCalledTimes(1);
    });

    const callArgs = mockRunPlanning.mock.calls[0][0];
    expect(callArgs).toHaveProperty('planning_date');
    expect(callArgs).toHaveProperty('horizon_days');
    expect(callArgs).toHaveProperty('workforce_state');
  });

  it('должен отображать состояние загрузки', () => {
    (useDsizPlanning as ReturnType<typeof vi.fn>).mockReturnValue({
      planningData: null,
      loading: true,
      error: null,
      runPlanning: mockRunPlanning,
      clearError: mockClearError,
    });

    render(
      <BrowserRouter>
        <DsizPlanningPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/Выполнение планирования/i)).toBeInTheDocument();
    const button = screen.getByRole('button', { name: /Запуск планирования/i });
    expect(button).toBeDisabled();
  });

  it('должен отображать ошибки', () => {
    const errorMessage = 'Ошибка выполнения планирования';
    (useDsizPlanning as ReturnType<typeof vi.fn>).mockReturnValue({
      planningData: null,
      loading: false,
      error: errorMessage,
      runPlanning: mockRunPlanning,
      clearError: mockClearError,
    });

    render(
      <BrowserRouter>
        <DsizPlanningPage />
      </BrowserRouter>
    );

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('должен отображать результаты планирования', () => {
    const mockPlanningData = {
      success: true,
      plan_id: 'test-plan-123',
      planning_date: '2026-01-26',
      horizon_days: 7,
      operations: [
        {
          bulk_product_sku: 'BULK-001',
          quantity_kg: 100,
          mode: 'CREAM_MODE',
          shift_date: '2026-01-27',
          shift_num: 1 as const,
          reactor_slot: 1 as const,
        },
      ],
      warnings: [],
      summary: {
        total_operations: 1,
        total_fg_products: 1,
        total_warnings: 0,
      },
    };

    (useDsizPlanning as ReturnType<typeof vi.fn>).mockReturnValue({
      planningData: mockPlanningData,
      loading: false,
      error: null,
      runPlanning: mockRunPlanning,
      clearError: mockClearError,
    });

    render(
      <BrowserRouter>
        <DsizPlanningPage />
      </BrowserRouter>
    );

    expect(screen.getByText('План производства')).toBeInTheDocument();
    expect(screen.getByText('Сводка планирования')).toBeInTheDocument();
  });

  it('должен отображать предупреждения', () => {
    const mockPlanningData = {
      success: true,
      plan_id: 'test-plan-123',
      planning_date: '2026-01-26',
      horizon_days: 7,
      operations: [],
      warnings: [
        {
          level: 'WARNING' as const,
          message: 'Недостаточно персонала для смены 1',
        },
      ],
      summary: {
        total_operations: 0,
        total_fg_products: 0,
        total_warnings: 1,
      },
    };

    (useDsizPlanning as ReturnType<typeof vi.fn>).mockReturnValue({
      planningData: mockPlanningData,
      loading: false,
      error: null,
      runPlanning: mockRunPlanning,
      clearError: mockClearError,
    });

    render(
      <BrowserRouter>
        <DsizPlanningPage />
      </BrowserRouter>
    );

    expect(screen.getByText('Предупреждения')).toBeInTheDocument();
    expect(screen.getByText(/Недостаточно персонала/i)).toBeInTheDocument();
  });

  it('должен отображать кнопку PDF Export только когда есть данные планирования', () => {
    const mockPlanningData = {
      success: true,
      plan_id: 'test-plan-123',
      planning_date: '2026-01-26',
      horizon_days: 7,
      operations: [],
      warnings: [],
      summary: {},
    };

    (useDsizPlanning as ReturnType<typeof vi.fn>).mockReturnValue({
      planningData: mockPlanningData,
      loading: false,
      error: null,
      runPlanning: mockRunPlanning,
      clearError: mockClearError,
    });

    render(
      <BrowserRouter>
        <DsizPlanningPage />
      </BrowserRouter>
    );

    const pdfButton = screen.getByRole('button', { name: /PDF Export/i });
    expect(pdfButton).toBeInTheDocument();
    expect(pdfButton).not.toBeDisabled();
  });
});

