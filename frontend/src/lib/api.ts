// Use relative base URL by default so Vite's dev proxy handles API requests during development
// Optionally allow overriding via VITE_API_BASE_URL for deployments
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL ?? '';

export interface User {
  id: number;
  username: string;
  email?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  email: string;
  phone_number?: string;
  full_name?: string;
  address?: string;
}

export interface InventoryItem {
  id: number;
  name: string;
  category: string;
  description: string;
  quantity: number;
  location: string;
  storage_box: string;
  brand: string;
  size: string;
  condition: string;
  image_data: string;
  created_at: string;
}

export interface AddItemRequest {
  name: string;
  category: string;
  description: string;
  quantity: number;
  location: string;
  storage_box: string;
  brand: string;
  size: string;
  condition: string;
  image: string; // base64 encoded
  username: string;
}

export interface SearchRequest {
  image: string; // base64 encoded
  username: string;
}

export interface ChatRequest {
  username: string;
  text: string;
}

class APIService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Authentication
  async login(credentials: LoginRequest): Promise<{ success: boolean; user_id: number; message: string }> {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async register(userData: RegisterRequest): Promise<{ success: boolean; user_id: number; message: string }> {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  // Items
  async addItem(itemData: AddItemRequest): Promise<{ success: boolean; item_id: number; ai_analysis: any }> {
    return this.request('/api/items/add', {
      method: 'POST',
      body: JSON.stringify(itemData),
    });
  }

  async getUserItems(username: string): Promise<{ success: boolean; items: InventoryItem[]; error?: string }> {
    return this.request(`/api/items/${username}`);
  }

  async deleteItem(itemId: number, username: string): Promise<{ success: boolean; message?: string; error?: string }> {
    return this.request(`/api/items/${itemId}?username=${username}`, {
      method: 'DELETE',
    });
  }

  // Search
  async searchItems(searchData: SearchRequest): Promise<{ success: boolean; results: any[] }> {
    return this.request('/api/search', {
      method: 'POST',
      body: JSON.stringify(searchData),
    });
  }

  // Chat
  async chatWithInventory(chatData: ChatRequest): Promise<{ success: boolean; response: string; sql_executed?: string }> {
    return this.request('/api/chat', {
      method: 'POST',
      body: JSON.stringify(chatData),
    });
  }

  // Health check
  async healthCheck(): Promise<{ message: string }> {
    return this.request('/');
  }
}

export const apiService = new APIService();
