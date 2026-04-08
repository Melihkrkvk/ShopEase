import { api } from './api';

export interface CartItem {
  id: number;
  cart_id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Order {
  id: number;
  user_id: number;
  payment_method: string;
  total: number;
  status: string;
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
}

export const orderService = {
  getCart: () => api.get<CartItem[]>('/cart'),

  addToCart: (product_id: number, quantity: number) =>
    api.post<CartItem>('/cart/items', { product_id, quantity }),

  removeFromCart: (product_id: number) =>
    api.delete<void>(`/cart/items/${product_id}`),

  placeOrder: (payment_method: string) =>
    api.post<Order>('/orders', { payment_method }),

  getOrders: () => api.get<Order[]>('/orders'),

  getOrder: (id: number) => api.get<Order>(`/orders/${id}`),

  getOrderItems: (id: number) => api.get<OrderItem[]>(`/orders/${id}/items`),

  getPaymentMethods: () => api.get<string[]>('/payment-methods'),
};
