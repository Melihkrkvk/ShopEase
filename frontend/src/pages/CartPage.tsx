import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { orderService } from '../services/orderService';
import type { CartItem } from '../services/orderService';
import { productService } from '../services/productService';
import type { Product } from '../services/productService';

interface CartPageProps {
  onCartChange: () => void;
}

export default function CartPage({ onCartChange }: CartPageProps) {
  const navigate = useNavigate();
  const [items, setItems] = useState<CartItem[]>([]);
  const [products, setProducts] = useState<Record<number, Product>>({});
  const [paymentMethod, setPaymentMethod] = useState('credit_card');
  const [paymentMethods, setPaymentMethods] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [placing, setPlacing] = useState(false);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const [cartItems, methods] = await Promise.all([
        orderService.getCart(),
        orderService.getPaymentMethods(),
      ]);
      setItems(cartItems);
      setPaymentMethods(methods);
      if (methods.length > 0) setPaymentMethod(methods[0]);

      const productMap: Record<number, Product> = {};
      await Promise.all(cartItems.map(async item => {
        const p = await productService.getById(item.product_id);
        productMap[item.product_id] = p;
      }));
      setProducts(productMap);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleRemove = async (productId: number) => {
    await orderService.removeFromCart(productId);
    await load();
    onCartChange();
  };

  const handlePlaceOrder = async () => {
    setError('');
    setPlacing(true);
    try {
      await orderService.placeOrder(paymentMethod);
      onCartChange();
      navigate('/orders');
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPlacing(false);
    }
  };

  const total = items.reduce((sum, i) => sum + i.total_price, 0);

  if (loading) return <div className="py-32 text-center text-gray-400 text-sm">Loading...</div>;

  return (
    <div className="max-w-3xl mx-auto py-8">
      <h1 className="text-gray-900 text-2xl font-bold mb-6">Your Cart</h1>

      {items.length === 0 ? (
        <div className="text-center py-32">
          <p className="text-gray-400 mb-4 text-sm">Your cart is empty.</p>
          <button onClick={() => navigate('/')} className="text-gray-900 font-semibold text-sm hover:underline">
            Continue shopping
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map(item => {
            const product = products[item.product_id];
            return (
              <div key={item.id} className="bg-white rounded-xl p-4 flex items-center gap-4 border border-gray-100">
                <div className="w-16 h-16 rounded-lg overflow-hidden bg-gray-100 shrink-0">
                  {product?.image_url ? (
                    <img src={product.image_url} alt={product.name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-300">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                      </svg>
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-gray-900 text-sm font-semibold truncate">{product?.name ?? `Product #${item.product_id}`}</p>
                  <p className="text-gray-400 text-xs mt-0.5">${item.unit_price.toFixed(2)} × {item.quantity}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-gray-900 font-bold">${item.total_price.toFixed(2)}</p>
                  <button
                    onClick={() => handleRemove(item.product_id)}
                    className="text-red-400 hover:text-red-600 text-xs mt-1 transition-colors"
                  >
                    Remove
                  </button>
                </div>
              </div>
            );
          })}

          {/* Summary */}
          <div className="bg-white border border-gray-100 rounded-xl p-5 mt-4 space-y-4">
            <div className="flex justify-between text-gray-900 font-bold text-lg">
              <span>Total</span>
              <span>${total.toFixed(2)}</span>
            </div>

            <div>
              <label className="block text-gray-500 text-xs mb-1.5 font-medium uppercase tracking-wider">Payment Method</label>
              <select
                value={paymentMethod}
                onChange={e => setPaymentMethod(e.target.value)}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-gray-900 text-sm focus:outline-none focus:border-gray-400 transition-colors bg-white"
              >
                {paymentMethods.map(m => (
                  <option key={m} value={m}>{m.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
                ))}
              </select>
            </div>

            {error && (
              <div className="border border-red-200 bg-red-50 text-red-600 text-sm px-3 py-2 rounded-lg">
                {error}
              </div>
            )}

            <button
              onClick={handlePlaceOrder}
              disabled={placing}
              className="w-full bg-gray-900 text-white font-bold py-3 rounded-xl hover:bg-gray-700 transition-colors disabled:opacity-50"
            >
              {placing ? 'Placing Order...' : 'Place Order'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
