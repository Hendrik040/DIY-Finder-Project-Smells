/**
 * Comprehensive unit tests for frontend/src/components/views/DashboardView.tsx
 * Testing dashboard component with focus on removed delete functionality
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DashboardView } from '../DashboardView';
import type { User, InventoryItem } from '@/lib/api';

// Mock the API service
vi.mock('@/lib/api', () => ({
  apiService: {
    getUserItems: vi.fn(),
    searchItems: vi.fn(),
    chat: vi.fn(),
  },
  type: {} as any
}));

describe('DashboardView', () => {
  const mockUser: User = {
    username: 'testuser',
    email: 'test@example.com'
  };

  const mockItems: InventoryItem[] = [
    {
      id: 1,
      name: 'Test Bolt',
      category: 'hardware',
      description: 'M6 x 20mm bolt',
      quantity: 10,
      location: 'garage',
      user_id: 'testuser'
    },
    {
      id: 2,
      name: 'Test Screw',
      category: 'hardware',
      description: 'Wood screw',
      quantity: 25,
      location: 'workshop',
      user_id: 'testuser'
    }
  ];

  const mockSetView = vi.fn();
  const mockOnRetryLoad = vi.fn();
  const mockOnLogout = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render dashboard with user information', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      expect(screen.getByText(mockUser.username)).toBeInTheDocument();
    });

    it('should render all items in the inventory', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      expect(screen.getByText('Test Bolt')).toBeInTheDocument();
      expect(screen.getByText('Test Screw')).toBeInTheDocument();
    });

    it('should render loading state correctly', () => {
      render(
        <DashboardView
          user={mockUser}
          items={[]}
          isLoading={true}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      expect(screen.getByRole('status')).toBeInTheDocument();
    });

    it('should render empty state when no items', () => {
      render(
        <DashboardView
          user={mockUser}
          items={[]}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      expect(screen.getByText(/no items/i)).toBeInTheDocument();
    });

    it('should display item quantities correctly', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      expect(screen.getByText(/10/)).toBeInTheDocument();
      expect(screen.getByText(/25/)).toBeInTheDocument();
    });

    it('should display item locations correctly', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      expect(screen.getByText(/garage/i)).toBeInTheDocument();
      expect(screen.getByText(/workshop/i)).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('should call onLogout when logout button is clicked', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      const logoutButton = screen.getByRole('button', { name: /logout/i });
      fireEvent.click(logoutButton);

      expect(mockOnLogout).toHaveBeenCalledTimes(1);
    });

    it('should navigate to add item view when add button is clicked', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      const addButton = screen.getByRole('button', { name: /add/i });
      fireEvent.click(addButton);

      expect(mockSetView).toHaveBeenCalledWith('add');
    });

    it('should render edit buttons for each item', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      expect(editButtons).toHaveLength(mockItems.length);
    });
  });

  describe('Deleted Delete Functionality', () => {
    it('should not have delete button functionality', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      // Delete buttons should be present in UI but not functional
      const deleteButtons = screen.getAllByRole('button', { name: /trash|delete/i });
      
      // Click a delete button
      fireEvent.click(deleteButtons[0]);

      // onRetryLoad should NOT be called (no deletion happened)
      expect(mockOnRetryLoad).not.toHaveBeenCalled();
    });

    it('should not show confirmation dialog for delete', () => {
      // Mock window.confirm
      const confirmSpy = vi.spyOn(window, 'confirm');
      
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      const deleteButtons = screen.getAllByRole('button', { name: /trash|delete/i });
      fireEvent.click(deleteButtons[0]);

      // Confirm should not be called since delete functionality is removed
      expect(confirmSpy).not.toHaveBeenCalled();
      
      confirmSpy.mockRestore();
    });

    it('should not call API deleteItem method', async () => {
      const { apiService } = await import('@/lib/api');
      
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      const deleteButtons = screen.getAllByRole('button', { name: /trash|delete/i });
      fireEvent.click(deleteButtons[0]);

      // Verify deleteItem was not called (it shouldn't exist)
      expect((apiService as any).deleteItem).toBeUndefined();
    });
  });

  describe('Item Display Features', () => {
    it('should display item categories as badges', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      expect(screen.getAllByText(/hardware/i).length).toBeGreaterThan(0);
    });

    it('should display item descriptions', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      expect(screen.getByText(/M6 x 20mm bolt/i)).toBeInTheDocument();
      expect(screen.getByText(/Wood screw/i)).toBeInTheDocument();
    });

    it('should handle items with missing optional fields', () => {
      const itemsWithMissingFields: InventoryItem[] = [
        {
          id: 3,
          name: 'Incomplete Item',
          category: 'misc',
          quantity: 1,
          user_id: 'testuser'
        } as InventoryItem
      ];

      render(
        <DashboardView
          user={mockUser}
          items={itemsWithMissingFields}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      expect(screen.getByText('Incomplete Item')).toBeInTheDocument();
    });
  });

  describe('View Navigation', () => {
    it('should have navigation to inventory view', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      const inventoryButton = screen.getByRole('button', { name: /inventory/i });
      fireEvent.click(inventoryButton);

      expect(mockSetView).toHaveBeenCalledWith(expect.any(String));
    });

    it('should have navigation to search view', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      const searchButton = screen.getByRole('button', { name: /search/i });
      fireEvent.click(searchButton);

      expect(mockSetView).toHaveBeenCalledWith(expect.any(String));
    });

    it('should have navigation to chat view', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      const chatButton = screen.getByRole('button', { name: /chat/i });
      fireEvent.click(chatButton);

      expect(mockSetView).toHaveBeenCalledWith(expect.any(String));
    });
  });

  describe('Error Handling', () => {
    it('should handle undefined items array', () => {
      render(
        <DashboardView
          user={mockUser}
          items={undefined as any}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      // Should not crash and should show empty state
      expect(screen.getByText(/no items/i)).toBeInTheDocument();
    });

    it('should handle null user gracefully', () => {
      const { container } = render(
        <DashboardView
          user={null as any}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      // Should render without crashing
      expect(container).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper button roles', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('should have accessible labels for action buttons', () => {
      render(
        <DashboardView
          user={mockUser}
          items={mockItems}
          isLoading={false}
          setView={mockSetView}
          onRetryLoad={mockOnRetryLoad}
          onLogout={mockOnLogout}
        />
      );

      // All icon buttons should have accessible labels or aria-labels
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(
          button.textContent || button.getAttribute('aria-label')
        ).toBeTruthy();
      });
    });
  });
});