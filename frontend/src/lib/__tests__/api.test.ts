/**
 * Comprehensive unit tests for frontend/src/lib/api.ts
 * Testing API service with focus on removed deleteItem method
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiService } from '../api';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch as any;

describe('APIService', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Authentication', () => {
    it('should successfully login a user', async () => {
      const mockResponse = {
        success: true,
        username: 'testuser',
        token: 'fake_token'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.login({
        username: 'testuser',
        password: 'password123'
      });

      expect(result.success).toBe(true);
      expect(result.username).toBe('testuser');
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/login'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: expect.any(String)
        })
      );
    });

    it('should handle login failure', async () => {
      const mockResponse = {
        success: false,
        error: 'Invalid credentials'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.login({
        username: 'testuser',
        password: 'wrongpassword'
      });

      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid credentials');
    });

    it('should successfully register a user', async () => {
      const mockResponse = {
        success: true,
        username: 'newuser'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.register({
        username: 'newuser',
        password: 'password123',
        email: 'user@example.com'
      });

      expect(result.success).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/register'),
        expect.objectContaining({
          method: 'POST'
        })
      );
    });

    it('should handle registration failure', async () => {
      const mockResponse = {
        success: false,
        error: 'Username already exists'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.register({
        username: 'existinguser',
        password: 'password123',
        email: 'user@example.com'
      });

      expect(result.success).toBe(false);
      expect(result.error).toBeTruthy();
    });
  });

  describe('Item Management', () => {
    it('should successfully create an item', async () => {
      const mockResponse = {
        success: true,
        item_id: 123
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.createItem({
        name: 'Test Bolt',
        category: 'hardware',
        description: 'M6 bolt',
        quantity: 10,
        location: 'garage',
        username: 'testuser'
      });

      expect(result.success).toBe(true);
      expect(result.item_id).toBe(123);
    });

    it('should handle item creation failure', async () => {
      const mockResponse = {
        success: false,
        error: 'Database error'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.createItem({
        name: 'Test Bolt',
        category: 'hardware',
        description: 'M6 bolt',
        quantity: 10,
        location: 'garage',
        username: 'testuser'
      });

      expect(result.success).toBe(false);
      expect(result.error).toBeTruthy();
    });

    it('should successfully retrieve user items', async () => {
      const mockItems = [
        {
          id: 1,
          name: 'Bolt',
          category: 'hardware',
          quantity: 10,
          location: 'garage'
        },
        {
          id: 2,
          name: 'Screw',
          category: 'hardware',
          quantity: 5,
          location: 'workshop'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          items: mockItems
        })
      });

      const result = await apiService.getUserItems('testuser');

      expect(result.success).toBe(true);
      expect(result.items).toHaveLength(2);
      expect(result.items[0].name).toBe('Bolt');
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/items/testuser'),
        expect.any(Object)
      );
    });

    it('should handle empty user items', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          items: []
        })
      });

      const result = await apiService.getUserItems('newuser');

      expect(result.success).toBe(true);
      expect(result.items).toHaveLength(0);
    });

    it('should handle error when retrieving user items', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.getUserItems('testuser')).rejects.toThrow();
    });
  });

  describe('Search', () => {
    it('should successfully search items', async () => {
      const mockResults = [
        {
          id: 1,
          score: 0.95,
          name: 'M6 Bolt',
          category: 'hardware'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          results: mockResults
        })
      });

      const result = await apiService.searchItems({
        query: 'M6 bolt',
        username: 'testuser'
      });

      expect(result.success).toBe(true);
      expect(result.results).toHaveLength(1);
      expect(result.results[0].name).toBe('M6 Bolt');
    });

    it('should handle search with no results', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          results: []
        })
      });

      const result = await apiService.searchItems({
        query: 'nonexistent',
        username: 'testuser'
      });

      expect(result.success).toBe(true);
      expect(result.results).toHaveLength(0);
    });

    it('should handle search error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: false,
          error: 'Search failed'
        })
      });

      const result = await apiService.searchItems({
        query: 'test',
        username: 'testuser'
      });

      expect(result.success).toBe(false);
    });
  });

  describe('Chat', () => {
    it('should successfully send chat message', async () => {
      const mockResponse = {
        success: true,
        response: 'You have 10 bolts in your inventory.'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await apiService.chat({
        username: 'testuser',
        message: 'How many bolts do I have?'
      });

      expect(result.success).toBe(true);
      expect(result.response).toContain('10 bolts');
    });

    it('should handle chat error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: false,
          error: 'Chat service unavailable'
        })
      });

      const result = await apiService.chat({
        username: 'testuser',
        message: 'Test message'
      });

      expect(result.success).toBe(false);
      expect(result.error).toBeTruthy();
    });
  });

  describe('Deleted Functionality', () => {
    it('should not have deleteItem method', () => {
      expect((apiService as any).deleteItem).toBeUndefined();
    });

    it('should not expose delete functionality in API', () => {
      const apiMethods = Object.getOwnPropertyNames(Object.getPrototypeOf(apiService));
      expect(apiMethods).not.toContain('deleteItem');
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.login({
        username: 'test',
        password: 'test'
      })).rejects.toThrow();
    });

    it('should handle non-OK HTTP responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      await expect(apiService.login({
        username: 'test',
        password: 'test'
      })).rejects.toThrow();
    });

    it('should handle malformed JSON responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        }
      });

      await expect(apiService.login({
        username: 'test',
        password: 'test'
      })).rejects.toThrow();
    });
  });

  describe('Request Configuration', () => {
    it('should include correct headers in requests', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      });

      await apiService.login({
        username: 'test',
        password: 'test'
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );
    });

    it('should use correct HTTP methods', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ success: true, items: [] })
      });

      // GET request
      await apiService.getUserItems('test');
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'GET'
        })
      );

      mockFetch.mockClear();

      // POST request
      await apiService.createItem({
        name: 'test',
        category: 'test',
        description: 'test',
        quantity: 1,
        location: 'test',
        username: 'test'
      });
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST'
        })
      );
    });
  });
});