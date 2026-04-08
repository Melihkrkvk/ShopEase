import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productService } from '../services/productService';
import type { Product } from '../services/productService';
import { orderService } from '../services/orderService';
import { authService } from '../services/authService';

interface ProductDetailPageProps {
  onCartChange: () => void;
}

export default function ProductDetailPage({ onCartChange }: ProductDetailPageProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [toast, setToast] = useState('');
  const [quantity, setQuantity] = useState(1);
  const isLoggedIn = authService.isLoggedIn();

  useEffect(() => {
    if (!id) return;
    productService.getById(parseInt(id)).then(p => {
      setProduct(p);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [id]);

  const handleAddToCart = async () => {
    if (!isLoggedIn) { navigate('/login'); return; }
    if (!product) return;
    setAdding(true);
    try {
      await orderService.addToCart(product.id, quantity);
      onCartChange();
      showToast(`${quantity} item${quantity > 1 ? 's' : ''} added to cart`);
    } catch (err) {
      showToast((err as Error).message);
    } finally {
      setAdding(false);
    }
  };

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 2500);
  };

  if (loading) return <div className="py-32 text-center text-gray-400 text-sm">Loading...</div>;

  if (!product) return (
    <div className="py-32 text-center">
      <p className="text-gray-500 mb-3">Product not found.</p>
      <button onClick={() => navigate('/')} className="text-sm font-medium text-gray-900 hover:underline">Back to products</button>
    </div>
  );

  return (
    <div className="py-8">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-xs text-gray-400 mb-8">
        <button onClick={() => navigate('/')} className="hover:text-gray-700 transition-colors">Home</button>
        <span>/</span>
        <button onClick={() => navigate(`/?category=${product.category}`)} className="hover:text-gray-700 capitalize transition-colors">{product.category}</button>
        <span>/</span>
        <span className="text-gray-700 truncate max-w-xs">{product.name}</span>
      </nav>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* Image */}
        <div className="aspect-square rounded-xl overflow-hidden bg-gray-100">
          {product.image_url ? (
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-cover"
              onError={e => {
                (e.target as HTMLImageElement).style.display = 'none';
                (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
              }}
            />
          ) : null}
          <div className={`w-full h-full flex items-center justify-center text-gray-300 ${product.image_url ? 'hidden' : ''}`}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-24 w-24" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </div>
        </div>

        {/* Info */}
        <div className="flex flex-col">
          <p className="text-xs text-gray-400 uppercase tracking-widest mb-2">{product.category}</p>
          <h1 className="text-gray-900 text-2xl font-bold leading-tight mb-4">{product.name}</h1>

          {product.description && (
            <p className="text-gray-500 text-sm leading-relaxed mb-6">{product.description}</p>
          )}

          <div className="mt-auto space-y-5">
            <div className="flex items-baseline gap-2">
              <span className="text-gray-900 text-3xl font-bold">${product.price.toFixed(2)}</span>
            </div>

            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${product.stock > 0 ? 'bg-green-500' : 'bg-red-400'}`} />
              <span className={`text-sm ${product.stock > 0 ? 'text-green-600' : 'text-red-500'}`}>
                {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
              </span>
            </div>

            {product.stock > 0 && (
              <>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-500">Quantity</span>
                  <div className="flex items-center border border-gray-200 rounded-lg overflow-hidden">
                    <button
                      onClick={() => setQuantity(q => Math.max(1, q - 1))}
                      className="w-9 h-9 flex items-center justify-center text-gray-500 hover:bg-gray-50 transition-colors"
                    >−</button>
                    <span className="w-10 text-center text-gray-900 text-sm font-semibold">{quantity}</span>
                    <button
                      onClick={() => setQuantity(q => Math.min(product.stock, q + 1))}
                      className="w-9 h-9 flex items-center justify-center text-gray-500 hover:bg-gray-50 transition-colors"
                    >+</button>
                  </div>
                </div>

                <button
                  onClick={handleAddToCart}
                  disabled={adding}
                  className="w-full bg-gray-900 text-white font-bold py-3.5 rounded-xl hover:bg-gray-700 transition-colors disabled:opacity-50"
                >
                  {adding ? 'Adding...' : 'Add to Cart'}
                </button>
              </>
            )}

            {!isLoggedIn && product.stock > 0 && (
              <p className="text-gray-400 text-xs text-center">
                <button onClick={() => navigate('/login')} className="text-gray-900 font-semibold hover:underline">Sign in</button> to add items to your cart
              </p>
            )}
          </div>
        </div>
      </div>

      {toast && (
        <div className="fixed bottom-6 right-6 bg-gray-900 text-white text-sm px-4 py-3 rounded-lg shadow-xl flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-[#e8c547]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          {toast}
        </div>
      )}
    </div>
  );
}
