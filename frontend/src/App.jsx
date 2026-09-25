import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import SearchHero from './components/SearchHero';
import FilterSidebar from './components/FilterSidebar';
import PropertyCard from './components/PropertyCard';
import { Home, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';

const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  // Se for relativo (ex: /api/v1), usa direto
  if (!envUrl || envUrl.startsWith('/')) {
    return envUrl || '/api/v1';
  }
  // Se foi compilado com localhost mas o usuário está acessando por IP remoto/hostname, usa proxy relativo do Nginx
  if (typeof window !== 'undefined' && envUrl.includes('localhost') && window.location.hostname !== 'localhost') {
    return '/api/v1';
  }
  return envUrl;
};

const API_BASE_URL = getApiBaseUrl();

export default function App() {
  const [filters, setFilters] = useState({
    city: 'Atibaia',
    state: 'SP',
    property_type: 'todos',
    check_in: '',
    check_out: '',
    guests: 10,
    min_price: '',
    max_price: '',
    has_pool: false,
    allows_pets: false,
    sort_by: 'price_asc',
    platforms: [],
    page: 1,
  });

  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProperties = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filters.city) params.append('city', filters.city);
      if (filters.state) params.append('state', filters.state);
      if (filters.property_type && filters.property_type !== 'todos') {
        params.append('property_type', filters.property_type);
      }
      if (filters.check_in) params.append('check_in', filters.check_in);
      if (filters.check_out) params.append('check_out', filters.check_out);
      if (filters.guests) params.append('guests', filters.guests.toString());
      if (filters.min_price) params.append('min_price', filters.min_price.toString());
      if (filters.max_price) params.append('max_price', filters.max_price.toString());
      if (filters.has_pool) params.append('has_pool', 'true');
      if (filters.allows_pets) params.append('allows_pets', 'true');
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      params.append('page', filters.page.toString());

      const url = `${API_BASE_URL}/search?${params.toString()}`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Erro ${response.status} ao consultar dados.`);
      }
      const data = await response.json();
      setResults(data);
    } catch (err) {
      console.error('Falha na busca:', err);
      setError(err.message || 'Erro ao conectar com o backend.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProperties();
  }, [filters.sort_by, filters.has_pool, filters.allows_pets, filters.property_type]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Header />

      <SearchHero
        filters={filters}
        setFilters={setFilters}
        onSearch={fetchProperties}
        isLoading={isLoading}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Barra Lateral de Filtros */}
          <div className="lg:col-span-1">
            <FilterSidebar filters={filters} setFilters={setFilters} />
          </div>

          {/* Listagem de Resultados */}
          <div className="lg:col-span-3 space-y-4">
            {/* Header da Busca */}
            <div className="flex items-center justify-between bg-white px-5 py-3 rounded-2xl border border-slate-200 shadow-xs">
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-slate-900 text-sm">
                  {results ? `${results.total_results} imóveis encontrados` : 'Buscando imóveis...'}
                </span>
                {results?.nights && (
                  <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-medium">
                    Período: {results.nights} {results.nights === 1 ? 'noite' : 'noites'}
                  </span>
                )}
                {results?.cached && (
                  <span className="text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-bold">
                    Cache Redis
                  </span>
                )}
              </div>

              <button
                onClick={fetchProperties}
                className="text-xs font-semibold text-slate-500 hover:text-slate-900 flex items-center gap-1.5 transition-colors"
                title="Recarregar cotações"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                <span>Atualizar</span>
              </button>
            </div>

            {/* Mensagem de Erro */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-2xl flex items-center gap-3 text-xs">
                <AlertCircle className="h-5 w-5 shrink-0 text-red-500" />
                <div>
                  <p className="font-bold">Não foi possível carregar os aluguéis</p>
                  <p className="mt-0.5 text-red-600">{error}</p>
                </div>
              </div>
            )}

            {/* Portais que não responderam */}
            {results?.failed_platforms?.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 text-amber-800 p-4 rounded-2xl flex items-center gap-3 text-xs">
                <AlertCircle className="h-5 w-5 shrink-0 text-amber-500" />
                <div>
                  <p>
                    <span className="font-bold">{results.failed_platforms.join(', ')}</span>{' '}
                    {results.failed_platforms.length > 1 ? 'não responderam' : 'não respondeu'} a tempo
                    (bloqueio ou lentidão do portal). A comparação abaixo considera apenas os demais portais.
                  </p>
                  {results.platform_errors && (
                    <p className="mt-1 font-mono text-[11px] text-amber-700">
                      {Object.entries(results.platform_errors)
                        .map(([name, reason]) => `${name}: ${reason}`)
                        .join(' · ')}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Skeleton Loading */}
            {isLoading && !results && (
              <div className="space-y-4">
                {[1, 2, 3].map((n) => (
                  <div key={n} className="bg-white rounded-2xl border border-slate-200 h-64 animate-pulse p-4" />
                ))}
              </div>
            )}

            {/* Lista de Imóveis */}
            {results && results.results && results.results.length > 0 ? (
              <div className="space-y-4">
                {results.results.map((prop) => (
                  <PropertyCard
                    key={prop.id}
                    property={prop}
                    nights={results.nights || 2}
                  />
                ))}
              </div>
            ) : (
              !isLoading && (
                <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-xs">
                  <div className="h-16 w-16 bg-slate-100 text-slate-400 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Home className="h-8 w-8" />
                  </div>
                  <h4 className="text-base font-bold text-slate-900">Nenhum imóvel encontrado</h4>
                  <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
                    Tente relaxar os filtros, buscar por outra cidade ou alterar o número de hóspedes.
                  </p>
                </div>
              )
            )}
          </div>
        </div>
      </main>

      {/* Rodapé */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <p>Verificador & Comparador de Aluguel de Temporada • Pronto para Docker & Homelab Portainer</p>
      </footer>
    </div>
  );
}
