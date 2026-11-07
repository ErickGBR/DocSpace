import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { api } from '../services/api';

export default function Spaces() {
  const { user, isGestor } = useAuth();
  const [spaces, setSpaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newSpace, setNewSpace] = useState({ title: '' });
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadSpaces();
  }, []);

  const loadSpaces = async () => {
    setLoading(true);
    try {
      const data = await api.getEspacios();
      setSpaces(data.results || data);
    } catch (e) {
      setError('Error cargando espacios');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newSpace.title.trim()) return;
    setCreating(true);
    try {
      const data = await api.createEspacio({ title: newSpace.title });
      setSpaces([...spaces, data]);
      setShowCreate(false);
      setNewSpace({ title: '' });
    } catch (e) {
      setError(e.data?.detail || 'Error creando espacio');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('¿Eliminar espacio?')) return;
    try {
      await api.deleteEspacio(id);
      setSpaces(spaces.filter(s => s.id !== id));
    } catch (e) {
      setError('Error eliminando espacio');
    }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full" /></div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Espacios de Trabajo</h1>
        {isGestor && (
          <button
            onClick={() => setShowCreate(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Nuevo Espacio
          </button>
        )}
      </div>

      {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded">{error}</div>}

      {showCreate && (
        <div className="mb-6 p-4 bg-white border border-gray-200 rounded-lg">
          <h3 className="font-semibold mb-4">Nuevo Espacio</h3>
          <form onSubmit={handleCreate} className="flex gap-2">
            <input
              type="text"
              value={newSpace.title}
              onChange={e => setNewSpace({ title: e.target.value })}
              placeholder="Nombre del espacio"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <button type="submit" disabled={creating} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
              {creating ? 'Creando...' : 'Crear'}
            </button>
            <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
              Cancelar
            </button>
          </form>
        </div>
      )}

      {spaces.length === 0 ? (
        <div className="text-center py-12">
          <svg className="mx-auto h-16 w-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No hay espacios</h3>
          <p className="mt-1 text-gray-500">{isGestor ? 'Crea tu primer espacio de trabajo' : 'No tienes acceso a ningún espacio'}</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {spaces.map(space => (
            <div key={space.id} className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-gray-900">{space.title}</h3>
                {isGestor && (
                  <button
                    onClick={() => handleDelete(space.id)}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Eliminar
                  </button>
                )}
              </div>
              <p className="text-sm text-gray-500 mb-3">Creado: {new Date(space.created_at).toLocaleDateString()}</p>
              <a
                href={`/dashboard?espacio=${space.id}`}
                className="inline-flex items-center px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition"
              >
                Abrir
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}