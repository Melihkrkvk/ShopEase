import { useNavigate } from 'react-router-dom';
import type { Product } from '../services/productService';

interface ProductCardProps {
  product: Product;
  onAddToCart: (productId: number) => void;
  isLoggedIn: boolean;
}

export default function ProductCard({ product, onAddToCart, isLoggedIn }: ProductCardProps) {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/products/${product.id}`)}
      className="bg-white rounded-lg overflow-hidden hover:shadow-md transition-shadow duration-200 cursor-pointer group flex flex-col"
    >
      {/* Image */}
      <div className="relative aspect-square overflow-hidden bg-gray-100">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            onError={e => {
              (e.target as HTMLImageElement).style.display = 'none';
              (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
            }}
          />
        ) : null}
        <div className={`w-full h-full flex items-center justify-center text-gray-300 ${product.image_url ? 'hidden' : ''}`}>
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
          </svg>
        </div>
        {product.stock === 0 && (
          <div className="absolute inset-0 bg-white/70 flex items-center justify-center">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">Out of Stock</span>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3 flex flex-col flex-1">
        <p className="text-[10px] text-gray-400 uppercase tracking-widest mb-1">{product.category}</p>
        <h3 className="text-gray-900 text-sm font-medium leading-snug mb-2 flex-1 line-clamp-2">{product.name}</h3>
        <div className="flex items-center justify-between mt-auto">
          <span className="text-gray-900 font-bold text-base">${product.price.toFixed(2)}</span>
          {isLoggedIn && product.stock > 0 && (
            <button
              onClick={e => { e.stopPropagation(); onAddToCart(product.id); }}
              className="bg-gray-900 text-white text-xs font-semibold px-3 py-1.5 rounded-full hover:bg-gray-700 active:scale-95 transition-all"
            >
              Add
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
