import { useState, useEffect } from 'react';
import { orderService } from '../services/orderService';
import type { Order, OrderItem } from '../services/orderService';
import { productService } from '../services/productService';
import type { Product } from '../services/productService';

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [orderItems, setOrderItems] = useState<Record<number, OrderItem[]>>({});
  const [products, setProducts] = useState<Record<number, Product>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    orderService.getOrders().then(data => {
      setOrders(data.sort((a, b) => b.id - a.id));
      setLoading(false);
    });
  }, []);

  const handleExpand = async (orderId: number) => {
    if (expandedId === orderId) { setExpandedId(null); return; }
    setExpandedId(orderId);
    if (orderItems[orderId]) return;

    const items = await orderService.getOrderItems(orderId);
    setOrderItems(prev => ({ ...prev, [orderId]: items }));

    const productMap: Record<number, Product> = { ...products };
    await Promise.all(
      items.filter(i => !productMap[i.product_id]).map(async i => {
        const p = await productService.getById(i.product_id);
        productMap[i.product_id] = p;
      })
    );
    setProducts(productMap);
  };

  const statusStyle = (status: string) => {
    if (status === 'pending') return 'text-yellow-700 bg-yellow-50 border border-yellow-200';
    if (status === 'completed') return 'text-green-700 bg-green-50 border border-green-200';
    return 'text-gray-600 bg-gray-50 border border-gray-200';
  };

  if (loading) return <div className="py-32 text-center text-gray-400 text-sm">Loading...</div>;

  return (
    <div className="max-w-3xl mx-auto py-8">
      <h1 className="text-gray-900 text-2xl font-bold mb-6">Order History</h1>

      {orders.length === 0 ? (
        <div className="text-center py-32 text-gray-400 text-sm">No orders yet.</div>
      ) : (
        <div className="space-y-3">
          {orders.map(order => (
            <div key={order.id} className="bg-white border border-gray-100 rounded-xl overflow-hidden">
              <button
                onClick={() => handleExpand(order.id)}
                className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <span className="text-gray-400 text-sm font-mono">#{order.id}</span>
                  <span className="text-gray-900 font-bold">${order.total.toFixed(2)}</span>
                  <span className="text-gray-400 text-xs capitalize">{order.payment_method.replace('_', ' ')}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded-full capitalize ${statusStyle(order.status)}`}>
                    {order.status}
                  </span>
                  <svg
                    className={`h-4 w-4 text-gray-400 transition-transform ${expandedId === order.id ? 'rotate-180' : ''}`}
                    fill="none" viewBox="0 0 24 24" stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {expandedId === order.id && (
                <div className="border-t border-gray-100 p-4 space-y-3">
                  {(orderItems[order.id] ?? []).map(item => {
                    const product = products[item.product_id];
                    return (
                      <div key={item.id} className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg overflow-hidden bg-gray-100 shrink-0">
                          {product?.image_url ? (
                            <img src={product.image_url} alt={product.name} className="w-full h-full object-cover" />
                          ) : (
                            <div className="w-full h-full bg-gray-100" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-gray-900 text-sm truncate">{product?.name ?? `Product #${item.product_id}`}</p>
                          <p className="text-gray-400 text-xs">${item.unit_price.toFixed(2)} × {item.quantity}</p>
                        </div>
                        <p className="text-gray-900 text-sm font-semibold shrink-0">
                          ${(item.unit_price * item.quantity).toFixed(2)}
                        </p>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
