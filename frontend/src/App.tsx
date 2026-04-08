import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ProductsPage from "./pages/ProductsPage";
import CartPage from "./pages/CartPage";
import OrdersPage from "./pages/OrdersPage";
import AdminProductsPage from "./pages/AdminProductsPage";
import ProductDetailPage from "./pages/ProductDetailPage";
import { authService } from "./services/authService";
import { orderService } from "./services/orderService";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  if (!authService.isLoggedIn()) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AppLayout() {
  const [cartCount, setCartCount] = useState(0);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(authService.isLoggedIn());

  const refreshCart = async () => {
    if (!authService.isLoggedIn()) {
      setCartCount(0);
      return;
    }
    try {
      const items = await orderService.getCart();
      setCartCount(items.length);
    } catch {
      setCartCount(0);
    }
  };

  const handleLogin = async () => {
    setIsLoggedIn(true);
    await refreshCart();
    try {
      const user = await authService.me();
      setIsAdmin(user.is_admin);
    } catch {}
  };

  const handleLogout = () => {
    authService.logout();
    setIsLoggedIn(false);
    setIsAdmin(false);
    setCartCount(0);
  };

  useEffect(() => {
    if (authService.isLoggedIn()) {
      refreshCart();
      authService.me().then((user) => setIsAdmin(user.is_admin)).catch(() => {});
    }
  }, []);

  return (
    <div className="min-h-screen bg-[#f5f5f5] flex flex-col">
      <Navbar cartCount={cartCount} isAdmin={isAdmin} isLoggedIn={isLoggedIn} onLogout={handleLogout} />
      <main className="flex-1 mx-4 my-8">
        <Routes>
          <Route path="/" element={<ProductsPage onCartChange={refreshCart} />} />
          <Route path="/cart" element={<ProtectedRoute><CartPage onCartChange={refreshCart} /></ProtectedRoute>} />
          <Route path="/orders" element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />
          <Route path="/admin/products" element={isAdmin ? <AdminProductsPage /> : <Navigate to="/" />} />
          <Route path="/products/:id" element={<ProductDetailPage onCartChange={refreshCart} />} />
          <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
          <Route path="/register" element={<RegisterPage onLogin={handleLogin} />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}
