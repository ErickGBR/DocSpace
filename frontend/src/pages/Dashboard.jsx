import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../hooks/useAuth';
import { api } from '../services/api';

export default function Dashboard() {
  const { user, logout, isGestor, isAdmin } = useAuth();
  const [documentos, setDocumentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('mis-documentos');
  const [uploading, setUploading] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  const cargarDocumentos = useCallback(async () => {
    setLoading(true);
    try {
      const params = activeTab === 'mis-documentos' ? {} : { espacio_trabajo_id: 1 };
      if (searchQuery) params.search = searchQuery;
      const data = await api.getDocumentos(params);
      setDocumentos(data.results || data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [activeTab, searchQuery]);

  useEffect(() => {
    cargarDocumentos();
  }, [cargarDocumentos]);

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-40 h-screen bg-white border-r border-gray-200 transition-all duration-300 ${
          sidebarOpen ? 'w-64' : 'w-20'
        }`}
      >
        {/* Brand */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
          <span className="font-bold text-lg text-gray-900 whitespace-nowrap overflow-hidden">
            {sidebarOpen ? 'DocSpace' : 'DS'}
          </span>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className={`p-2 rounded-lg hover:bg-gray-100 transition ${
              sidebarOpen ? 'ml-auto' : 'mx-auto'
            }`}
            aria-label="Toggle sidebar"
          >
            <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={sidebarOpen ? 'M11 19l-7-7 7-7m8 14l-7-7 7-7' : 'M13 5l7 7-7 7M5 5l7 7-7 7'} />
            </svg>
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1" aria-label="Main navigation">
          <NavItem
            icon={<FolderIcon />}
            label="Mis Documentos"
            active={activeTab === 'mis-documentos'}
            onClick={() => setActiveTab('mis-documentos')}
            sidebarOpen={sidebarOpen}
          />
          <NavItem
            icon={<GlobeIcon />}
            label="Todos los Documentos"
            active={activeTab === 'todos'}
            onClick={() => setActiveTab('todos')}
            sidebarOpen={sidebarOpen}
          />
          {isGestor && (
            <NavItem
              icon={<HistoryIcon />}
              label="Historial"
              active={activeTab === 'historial'}
              onClick={() => setActiveTab('historial')}
              sidebarOpen={sidebarOpen}
            />
          )}
        </nav>

        {/* User info at bottom */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
          {sidebarOpen && (
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-medium">
                {user?.nombre_usuario?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{user?.nombre_usuario}</p>
                <p className="text-xs text-gray-500 truncate capitalize">{user?.rol?.nombre || 'Usuario'}</p>
              </div>
              <button
                onClick={logout}
                className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition"
                title="Cerrar sesión"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
        {/* Top Bar */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 sticky top-0 z-30">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-semibold text-gray-900">
              {activeTab === 'mis-documentos' ? 'Mis Documentos' : activeTab === 'todos' ? 'Todos los Documentos' : 'Historial'}
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            {/* Search */}
            <div className="relative hidden sm:block">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Buscar documentos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-64 pl-10 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-gray-50"
              />
            </div>

            {/* Upload Button */}
            {isGestor && activeTab !== 'historial' && (
              <label className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 cursor-pointer transition">
                <UploadIcon className="w-5 h-5" />
                <span>Subir</span>
                <input
                  type="file"
                  className="sr-only"
                  accept=".txt,.md,.js,.ts,.jsx,.tsx,.json,.xml,.html,.css,.scss,.sql,.py,.java,.cpp,.c,.h,.cs,.php,.rb,.go,.rs,.sh,.bat,.ps1,.yaml,.yml,.toml,.ini,.cfg,.conf,.log,.csv,.rtf"
                  onChange={(e) => {
                    const file = e.target.files[0];
                    if (file && !esArchivoTexto(file)) {
                      alert('Solo se permiten archivos de texto (txt, md, js, ts, json, xml, html, css, sql, py, etc.)');
                      e.target.value = '';
                      return;
                    }
                    setUploadFile(file);
                  }}
                />
              </label>
            )}
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 p-6 overflow-auto">
          {activeTab === 'historial' ? (
            <HistorialView />
          ) : (
            <DocumentosView
              documentos={documentos}
              loading={loading}
              onDelete={() => {}}
              formatSize={() => ''}
              formatDate={() => ''}
              getFileIcon={() => ''}
              isGestor={isGestor}
            />
          )}
        </main>
      </div>
    </div>
  );
}

function NavItem({ icon, label, active, onClick, sidebarOpen }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition ${
        active
          ? 'bg-blue-50 text-blue-700'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
      }`}
    >
      <span className="flex-shrink-0 w-5 h-5">{icon}</span>
      {sidebarOpen && <span className="font-medium truncate">{label}</span>}
    </button>
  );
}

function DocumentosView({ documentos, loading, onDelete, formatSize, formatDate, getFileIcon, isGestor }) {
  return <div>DocumentosView placeholder</div>;
}

function HistorialView() {
  return <div>HistorialView placeholder</div>;
}

// SVG Icons
function FolderIcon() {
  return (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
    </svg>
  );
}

function GlobeIcon() {
  return (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
    </svg>
  );
}

function HistoryIcon() {
  return (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  );
}

function EyeIcon() {
  return (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  );
}

function TrashIcon() {
  return (
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-5 h-5">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  );
}