import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { api } from '../services/api';

export default function Document() {
  const { user, logout, isGestor, isAdmin } = useAuth();
  const navigate = useNavigate();
  const { id, espacio } = useParams();
  const [documento, setDocumento] = useState(null);
  const [loading, setLoading] = useState(true);
  const [content, setContent] = useState('');
  const [saving, setSaving] = useState(false);
  const [versions, setVersions] = useState([]);
  const [versionsLoading, setVersionsLoading] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const [comparing, setComparing] = useState({ v1: '', v2: '' });
  const [diff, setDiff] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDocument();
  }, [id, espacio]);

  const loadDocument = async () => {
    setLoading(true);
    try {
      const [docData, versionsData] = await Promise.all([
        api.getDocumentos({ id }).then(d => d.results?.[0] || d).catch(() => null),
        api.getDocumentoVersions(id).catch(() => [])
      ]);
      if (docData) {
        setDocumento(docData);
        const content = await api.getDocumentoContent(id);
        setContent(content.content || '');
      }
      setVersions(versionsData.results || versionsData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!documento) return;
    setSaving(true);
    try {
      await api.saveDocumento(documento.id, content);
      alert('Documento guardado');
      loadDocument();
    } catch (e) {
      alert(e.data?.detail || 'Error guardando');
    } finally {
      setSaving(false);
    }
  };

  const handleCompare = async () => {
    if (!comparing.v1 || !comparing.v2) return;
    try {
      const data = await api.get(`/documentos/${id}/compare/`, { v1: comparing.v1, v2: comparing.v2 });
      setDiff(data.diff);
    } catch (e) {
      alert('Error comparando versiones');
    }
  };

  const handleRestore = async (version) => {
    if (!confirm(`¿Restaurar versión ${version}?`)) return;
    try {
      await api.post(`/documentos/${id}/restore/`, { version });
      alert('Documento restaurado');
      loadDocument();
    } catch (e) {
      alert('Error restaurando');
    }
  };

  const formatDate = (iso) => {
    if (!iso) return '-';
    return new Date(iso).toLocaleDateString('es-ES', {
      day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  };

  const formatSize = (bytes) => {
    if (!bytes) return '-';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64"><div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full" /></div>;
  }

  if (!documento) {
    return <div className="text-center py-16"><h3 className="text-lg font-medium text-gray-900">Documento no encontrado</h3></div>;
  }

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside className="fixed top-0 left-0 z-40 h-screen bg-white border-r border-gray-200 w-64">
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
          <span className="font-bold text-lg text-gray-900">DocSpace</span>
        </div>
        <nav className="p-4 space-y-1">
          <button onClick={() => navigate(`/dashboard?espacio=${espacio}`)} className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
            <span className="font-medium truncate">Volver</span>
          </button>
          <hr className="my-2 border-gray-200" />
          <div className="px-3 py-2 bg-blue-50 rounded-lg mb-2">
            <p className="text-xs font-medium text-blue-700 uppercase tracking-wider">Documento</p>
            <p className="font-medium text-gray-900 truncate">{documento?.nombre_documento}</p>
          </div>
        </nav>
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          <button onClick={logout} className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-500 hover:bg-gray-100 transition">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
            <span className="font-medium">Cerrar sesión</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col ml-64">
        {/* Top Bar */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-30">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold text-gray-900">{documento?.nombre_documento}</h1>
            <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded">{documento?.espacio_trabajo}</span>
          </div>
          <div className="flex items-center space-x-4">
            <button onClick={() => setShowVersions(!showVersions)} className="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition">
              Versiones ({versions.length})
            </button>
            <button onClick={handleSave} disabled={saving} className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition disabled:opacity-50">
              {saving ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 p-6 overflow-auto">
          {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded">{error}</div>}

          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <textarea
              value={content}
              onChange={e => setContent(e.target.value)}
              className="w-full h-96 p-4 font-mono text-sm border-none focus:outline-none resize-none"
              placeholder="Escribe aquí..."
              spellCheck={false}
            />
          </div>

          {/* Versions Panel */}
          {showVersions && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={() => setShowVersions(false)}>
              <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh]" onClick={e => e.stopPropagation()}>
                <div className="flex items-center justify-between p-4 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-900">Historial de Versiones</h3>
                  <button onClick={() => setShowVersions(false)} className="p-1 rounded-lg hover:bg-gray-100 text-gray-500 transition">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                </div>
                <div className="max-h-[60vh] overflow-y-auto">
                  {versions.length === 0 ? (
                    <div className="text-center py-16"><p className="text-gray-500">Sin versiones</p></div>
                  ) : (
                    <div className="divide-y divide-gray-200">
                      {versions.map((v, i) => (
                        <div key={v.id || i} className="p-4 hover:bg-gray-50 flex items-center justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{v.accion || 'Versión'}</p>
                            <p className="text-sm text-gray-500">{formatDate(v.created_at)} por {v.usuario_nombre || 'Desconocido'}</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <button onClick={() => setComparing({...comparing, v1: v.version_epoch || i})} className="px-2 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded hover:bg-blue-100">Comparar</button>
                            <button onClick={() => handleRestore(v.version_epoch || i)} className="px-2 py-1 text-xs font-medium text-green-600 bg-green-50 rounded hover:bg-green-100">Restaurar</button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

function formatDate(iso) {
  if (!iso) return '-';
  return new Date(iso).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}