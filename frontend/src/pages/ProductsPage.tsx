import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { productService } from '../services/productService';
import type { Product } from '../services/productService';
import { orderService } from '../services/orderService';
import { authService } from '../services/authService';
import ProductCard from '../components/ProductCard';

interface ProductsPageProps {
  onCartChange: () => void;
}

export default function ProductsPage({ onCartChange }: ProductsPageProps) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState('');
  const isLoggedIn = authService.isLoggedIn();

  const search = searchParams.get('search') ?? '';
  const category = searchParams.get('category') ?? '';

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const params: { search?: string; category?: string } = {};
        if (search) params.search = search;
        if (category) params.category = category;
        const data = await productService.getAll(params);
        setProducts(data);
      } finally {
        setLoading(false);
      }
    };
    const timer = setTimeout(load, 200);
    return () => clearTimeout(timer);
  }, [search, category]);

  const handleAddToCart = async (productId: number) => {
    if (!isLoggedIn) { navigate('/login'); return; }
    try {
      await orderService.addToCart(productId, 1);
      onCartChange();
      showToast('Added to cart');
    } catch (err) {
      showToast((err as Error).message);
    }
  };

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 2500);
  };

  return (
    <div className="py-6">
      {/* Active filter indicator */}
      {(search || category) && (
        <div className="flex items-center gap-3 mb-5">
          <span className="text-sm text-gray-500">
            {search && <><strong className="text-gray-900">"{search}"</strong> için sonuçlar</>}
            {category && !search && <><strong className="text-gray-900 capitalize">{category}</strong></>}
          </span>
          <button
            onClick={() => navigate('/')}
            className="text-xs text-gray-400 hover:text-gray-700 underline transition-colors"
          >
            Clear
          </button>
        </div>
      )}

      {/* Grid */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="bg-white rounded-lg overflow-hidden animate-pulse">
              <div className="aspect-square bg-gray-100" />
              <div className="p-3 space-y-2">
                <div className="h-2 bg-gray-100 rounded w-1/3" />
                <div className="h-3 bg-gray-100 rounded w-4/5" />
                <div className="h-4 bg-gray-100 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-32">
          <p className="text-gray-400 text-sm">No products found.</p>
          {(search || category) && (
            <button onClick={() => navigate('/')} className="text-gray-900 text-sm mt-2 hover:underline font-medium">
              View all products
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {products.map(p => (
            <ProductCard
              key={p.id}
              product={p}
              onAddToCart={handleAddToCart}
              isLoggedIn={isLoggedIn}
            />
          ))}
        </div>
      )}

      {/* Toast */}
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
