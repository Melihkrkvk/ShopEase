import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

interface NavbarProps {
  cartCount: number;
  isAdmin: boolean;
  isLoggedIn: boolean;
  onLogout: () => void;
}

const CATEGORIES = [
  { label: "All", value: "" },
  { label: "Turntables", value: "turntables" },
  { label: "Vinyl", value: "vinyl" },
  { label: "Cartridges", value: "cartridges" },
  { label: "Preamps", value: "preamps" },
  { label: "Accessories", value: "accessories" },
];

export default function Navbar({ cartCount, isAdmin, isLoggedIn, onLogout }: NavbarProps) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [search, setSearch] = useState("");
  const activeCategory = searchParams.get('category') ?? '';

  const handleLogout = () => {
    onLogout();
    navigate("/login");
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (search.trim())
      navigate(`/?search=${encodeURIComponent(search.trim())}`);
    else navigate("/");
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      {/* Top row — same max-width as main */}
      <div className="mx-auto px-4 h-20 flex items-center gap-8 justify-between">
        <Link
          to="/"
          className="shrink-0 text-3xl font-black tracking-tight text-gray-900 group"
        >
          Shop
          <span className="text-[#e8c547] group-hover:text-yellow-500 transition-colors">
            Ease
          </span>
        </Link>

        {/* Search */}
        <form
          onSubmit={handleSearch}
          className="flex-1 max-w-xl hidden md:block"
        >
          <div className="relative">
            <svg
              className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400 pointer-events-none"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search for anything..."
              className="w-full h-11 bg-gray-50 border border-gray-200 rounded-xl pl-11 pr-4 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#e8c547]/30 focus:border-[#e8c547] focus:bg-white transition-all"
            />
          </div>
        </form>

        {/* Right actions */}
        <div className="flex items-center gap-1 ml-auto shrink-0">
          {isLoggedIn ? (
            <>
              {isAdmin && (
                <Link to="/admin/products" className="group flex flex-col items-center justify-center w-14 h-14 rounded-xl transition-colors gap-1">
                  <svg className="h-6 w-6 text-gray-500 group-hover:text-[#e8c547] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span className="text-xs font-medium text-gray-500 leading-none">Admin</span>
                </Link>
              )}

              <Link to="/orders" className="group flex flex-col items-center justify-center w-14 h-14 rounded-xl transition-colors gap-1">
                <svg className="h-6 w-6 text-gray-500 group-hover:text-[#e8c547] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <span className="text-xs font-medium text-gray-500 leading-none">Orders</span>
              </Link>

              <Link to="/cart" className="group flex flex-col items-center justify-center w-14 h-14 rounded-xl transition-colors gap-1">
                <div className="relative">
                  <svg className="h-6 w-6 text-gray-500 group-hover:text-[#e8c547] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                  </svg>
                  {cartCount > 0 && (
                    <span className="absolute -top-2 -right-2 bg-gray-900 text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center ring-2 ring-white">
                      {cartCount}
                    </span>
                  )}
                </div>
                <span className="text-xs font-medium text-gray-500 leading-none">Cart</span>
              </Link>

              <button onClick={handleLogout} className="group flex flex-col items-center justify-center w-14 h-14 rounded-xl transition-colors gap-1">
                <svg className="h-6 w-6 text-gray-500 group-hover:text-[#e8c547] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span className="text-xs font-medium text-gray-500 leading-none">Logout</span>
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="group flex flex-col items-center justify-center w-14 h-14 rounded-xl transition-colors gap-1">
                <svg className="h-6 w-6 text-gray-500 group-hover:text-[#e8c547] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
                <span className="text-xs font-medium text-gray-500 leading-none">Login</span>
              </Link>
              <Link to="/register" className="group flex flex-col items-center justify-center w-14 h-14 rounded-xl transition-colors gap-1">
                <svg className="h-6 w-6 text-gray-500 group-hover:text-[#e8c547] transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
                <span className="text-xs font-medium text-gray-500 leading-none">Register</span>
              </Link>
            </>
          )}
        </div>
      </div>

      {/* Category bar */}
      <div className="border-t border-gray-100">
        <nav className="flex items-center overflow-x-auto">
          {CATEGORIES.map((cat) => {
            const isActive = cat.value === activeCategory;
            return (
              <Link
                key={cat.value}
                to={cat.value ? `/?category=${cat.value}` : "/"}
                className={`shrink-0 px-4 py-3.5 text-xs font-bold uppercase tracking-widest border-b-2 transition-all whitespace-nowrap ${
                  isActive
                    ? 'text-gray-900 border-[#e8c547]'
                    : 'text-gray-500 border-transparent hover:text-gray-900 hover:border-[#e8c547]'
                }`}
              >
                {cat.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
