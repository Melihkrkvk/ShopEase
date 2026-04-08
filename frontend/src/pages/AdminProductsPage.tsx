import { useState, useEffect } from 'react';
import { productService } from '../services/productService';
import type { Product, ProductCreate } from '../services/productService';

const EMPTY_FORM: ProductCreate = { name: '', price: 0, stock: 0, category: '', image_url: '', description: '' };

export default function AdminProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<ProductCreate>(EMPTY_FORM);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const load = async () => {
    const data = await productService.getAll();
    setProducts(data);
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const openCreate = () => { setForm(EMPTY_FORM); setEditId(null); setError(''); setShowForm(true); };
  const openEdit = (p: Product) => {
    setForm({ name: p.name, price: p.price, stock: p.stock, category: p.category, image_url: p.image_url ?? '', description: p.description ?? '' });
    setEditId(p.id);
    setError('');
    setShowForm(true);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      const data = { ...form, image_url: form.image_url || undefined, description: form.description || undefined };
      if (editId) {
        await productService.update(editId, data);
      } else {
        await productService.create(data);
      }
      setShowForm(false);
      load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this product?')) return;
    await productService.delete(id);
    load();
  };

  if (loading) return <div className="py-32 text-center text-gray-400 text-sm">Loading...</div>;

  return (
    <div className="py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-gray-900 text-2xl font-bold">Products</h1>
        <button onClick={openCreate} className="bg-gray-900 text-white font-semibold px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors text-sm">
          + Add Product
        </button>
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md border border-gray-100">
            <h3 className="text-gray-900 font-bold text-lg mb-4">{editId ? 'Edit Product' : 'Add Product'}</h3>
            <form onSubmit={handleSubmit} className="space-y-3">
              {error && <div className="border border-red-200 bg-red-50 text-red-600 text-sm px-3 py-2 rounded-lg">{error}</div>}
              {(['name', 'category', 'image_url', 'description'] as const).map(field => (
                <div key={field}>
                  <label className="block text-gray-500 text-xs font-medium mb-1 capitalize">{field.replace('_', ' ')}</label>
                  <input
                    type="text"
                    value={form[field] as string}
                    onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))}
                    required={field === 'name' || field === 'category'}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-gray-900 text-sm focus:outline-none focus:border-gray-400 transition-colors"
                  />
                </div>
              ))}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-500 text-xs font-medium mb-1">Price ($)</label>
                  <input type="number" step="0.01" min="0" value={form.price}
                    onChange={e => setForm(f => ({ ...f, price: parseFloat(e.target.value) }))}
                    required className="w-full border border-gray-200 rounded-lg px-3 py-2 text-gray-900 text-sm focus:outline-none focus:border-gray-400 transition-colors" />
                </div>
                <div>
                  <label className="block text-gray-500 text-xs font-medium mb-1">Stock</label>
                  <input type="number" min="0" value={form.stock}
                    onChange={e => setForm(f => ({ ...f, stock: parseInt(e.target.value) }))}
                    required className="w-full border border-gray-200 rounded-lg px-3 py-2 text-gray-900 text-sm focus:outline-none focus:border-gray-400 transition-colors" />
                </div>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="submit" disabled={saving} className="flex-1 bg-gray-900 text-white font-bold py-2 rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50">
                  {saving ? 'Saving...' : 'Save'}
                </button>
                <button type="button" onClick={() => setShowForm(false)} className="flex-1 border border-gray-200 text-gray-600 font-semibold py-2 rounded-lg hover:bg-gray-50 transition-colors">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="bg-white border border-gray-100 rounded-xl overflow-hidden shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              <th className="text-left text-gray-500 font-medium px-4 py-3 text-xs uppercase tracking-wider">Product</th>
              <th className="text-left text-gray-500 font-medium px-4 py-3 text-xs uppercase tracking-wider">Category</th>
              <th className="text-right text-gray-500 font-medium px-4 py-3 text-xs uppercase tracking-wider">Price</th>
              <th className="text-right text-gray-500 font-medium px-4 py-3 text-xs uppercase tracking-wider">Stock</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {products.map(p => (
              <tr key={p.id} className="border-b border-gray-100 last:border-0 hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    {p.image_url ? (
                      <img src={p.image_url} alt={p.name} className="w-8 h-8 object-cover rounded-lg bg-gray-100" />
                    ) : (
                      <div className="w-8 h-8 bg-gray-100 rounded-lg" />
                    )}
                    <span className="text-gray-900 font-medium truncate max-w-xs">{p.name}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-xs uppercase tracking-wider text-gray-400">{p.category}</td>
                <td className="px-4 py-3 text-gray-900 text-right font-medium">${p.price.toFixed(2)}</td>
                <td className="px-4 py-3 text-right">
                  <span className={p.stock > 0 ? 'text-green-600 font-medium' : 'text-red-500 font-medium'}>{p.stock}</span>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex gap-3 justify-end">
                    <button onClick={() => openEdit(p)} className="text-gray-400 hover:text-gray-900 text-xs font-medium transition-colors">Edit</button>
                    <button onClick={() => handleDelete(p.id)} className="text-red-400 hover:text-red-600 text-xs font-medium transition-colors">Delete</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
