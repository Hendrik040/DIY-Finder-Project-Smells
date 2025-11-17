/**
 * Comprehensive unit tests for frontend/src/lib/api.ts
 * 
 * Tests cover:
 * - Removed deleteItem method
 * - API service functionality
 * - Error handling
 * - Request/response handling
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { apiService, type SearchRequest } from '../lib/api';

// Mock fetch globally
global.fetch = vi.fn();

describe('APIService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('deleteItem method removal', () => {
    it('should not have deleteItem method', () => {
      expect(apiService).not.toHaveProperty('deleteItem');
      expect(typeof (apiService as any).deleteItem).toBe('undefined');
    });
  });

  describe('request method', () => {
    it('should make successful GET request', async () => {
      const mockResponse = { success: true, data: { test: 'value' } };
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.request('/test');

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          method: 'GET',
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should make successful POST request', async () => {
      const mockResponse = { success: true };
      const postData = { username: 'test', password: 'pass' };
      
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.request('/test', {
        method: 'POST',
        body: JSON.stringify(postData),
      });

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle network errors', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.request('/test')).rejects.toThrow('Network error');
    });

    it('should handle HTTP errors', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      });

      await expect(apiService.request('/test')).rejects.toThrow('HTTP error! status: 404');
    });

    it('should include proper headers', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      await apiService.request('/test');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });
  });

  describe('login', () => {
    it('should login successfully', async () => {
      const mockResponse = {
        success: true,
        user: { username: 'testuser', email: 'test@example.com' },
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.login('testuser', 'password123');

      expect(result.success).toBe(true);
      expect(result.user?.username).toBe('testuser');
    });

    it('should handle login failure', async () => {
      const mockResponse = {
        success: false,
        error: 'Invalid credentials',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.login('testuser', 'wrongpass');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Invalid credentials');
    });
  });

  describe('register', () => {
    it('should register successfully', async () => {
      const mockResponse = {
        success: true,
        user: { username: 'newuser', email: 'new@example.com' },
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.register(
        'newuser',
        'password123',
        'new@example.com'
      );

      expect(result.success).toBe(true);
      expect(result.user?.username).toBe('newuser');
    });

    it('should handle registration with existing username', async () => {
      const mockResponse = {
        success: false,
        error: 'Username already exists',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.register(
        'existing',
        'password123',
        'test@example.com'
      );

      expect(result.success).toBe(false);
      expect(result.error).toContain('already exists');
    });
  });

  describe('getUserItems', () => {
    it('should fetch user items successfully', async () => {
      const mockItems = [
        {
          id: 1,
          name: 'Hammer',
          category: 'Tools',
          quantity: 1,
          user_id: 'testuser',
        },
        {
          id: 2,
          name: 'Screwdriver',
          category: 'Tools',
          quantity: 2,
          user_id: 'testuser',
        },
      ];

      const mockResponse = {
        success: true,
        items: mockItems,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.getUserItems('testuser');

      expect(result.success).toBe(true);
      expect(result.items).toHaveLength(2);
      expect(result.items[0].name).toBe('Hammer');
    });

    it('should handle empty inventory', async () => {
      const mockResponse = {
        success: true,
        items: [],
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.getUserItems('testuser');

      expect(result.success).toBe(true);
      expect(result.items).toHaveLength(0);
    });

    it('should handle fetch error', async () => {
      const mockResponse = {
        success: false,
        error: 'Database error',
        items: [],
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.getUserItems('testuser');

      expect(result.success).toBe(false);
      expect(result.error).toBe('Database error');
    });
  });

  describe('searchItems', () => {
    it('should search items successfully', async () => {
      const searchData: SearchRequest = {
        query: 'M6 bolt',
        username: 'testuser',
      };

      const mockResults = [
        {
          id: 1,
          name: 'M6 Bolt',
          category: 'Hardware',
          score: 0.95,
        },
      ];

      const mockResponse = {
        success: true,
        results: mockResults,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.searchItems(searchData);

      expect(result.success).toBe(true);
      expect(result.results).toHaveLength(1);
      expect(result.results[0].name).toBe('M6 Bolt');
    });

    it('should handle empty search results', async () => {
      const searchData: SearchRequest = {
        query: 'nonexistent item',
        username: 'testuser',
      };

      const mockResponse = {
        success: true,
        results: [],
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.searchItems(searchData);

      expect(result.success).toBe(true);
      expect(result.results).toHaveLength(0);
    });
  });

  describe('createItem', () => {
    it('should create item with file upload', async () => {
      const mockFile = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
      const itemData = {
        name: 'Hammer',
        category: 'Tools',
        description: 'A hammer',
        quantity: 1,
      };

      const mockResponse = {
        success: true,
        item_id: 1,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.createItem('testuser', itemData, mockFile);

      expect(result.success).toBe(true);
      expect(result.item_id).toBe(1);
    });

    it('should create item without file', async () => {
      const itemData = {
        name: 'Hammer',
        category: 'Tools',
        description: 'A hammer',
        quantity: 1,
      };

      const mockResponse = {
        success: true,
        item_id: 1,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.createItem('testuser', itemData);

      expect(result.success).toBe(true);
      expect(result.item_id).toBe(1);
    });
  });

  describe('chat', () => {
    it('should send chat message successfully', async () => {
      const mockResponse = {
        success: true,
        response: 'You have 5 items in your inventory',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.chat('testuser', 'Show me my items');

      expect(result.success).toBe(true);
      expect(result.response).toContain('5 items');
    });

    it('should handle chat errors', async () => {
      const mockResponse = {
        success: false,
        error: 'Invalid query',
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await apiService.chat('testuser', 'invalid; DROP TABLE;');

      expect(result.success).toBe(false);
      expect(result.error).toBeTruthy();
    });
  });
});