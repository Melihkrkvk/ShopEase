import { api } from './api';

export interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
  category: string;
  image_url: string | null;
  description: string | null;
}

export interface ProductCreate {
  name: string;
  price: number;
  stock: number;
  category: string;
  image_url?: string;
  description?: string;
}

export const productService = {
  getAll: (params?: { search?: string; category?: string }) => {
    const qs = new URLSearchParams();
    if (params?.search) qs.set('search', params.search);
    if (params?.category) qs.set('category', params.category);
    const query = qs.toString() ? `?${qs.toString()}` : '';
    return api.get<Product[]>(`/products${query}`);
  },

  getById: (id: number) => api.get<Product>(`/products/${id}`),

  create: (data: ProductCreate) => api.post<Product>('/products', data),

  update: (id: number, data: Partial<ProductCreate>) =>
    api.put<Product>(`/products/${id}`, data),

  delete: (id: number) => api.delete<void>(`/products/${id}`),
};
