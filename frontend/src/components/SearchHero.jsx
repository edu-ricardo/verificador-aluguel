import React from 'react';
import { Search, MapPin, Calendar, Users, SlidersHorizontal } from 'lucide-react';

export default function SearchHero({ filters, setFilters, onSearch, isLoading }) {
  const quickCities = ['Atibaia', 'Ibiúna', 'Mairiporã', 'São Roque', 'Brotas', 'Ubatuba'];

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch();
  };

  return (
    <div className="bg-gradient-to-b from-brand-50/70 to-slate-50 border-b border-slate-200 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-6">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Compare preços de chácaras e sítios em múltiplos portais
          </h2>
          <p className="mt-2 text-sm text-slate-600">
            Descubra onde o mesmo imóvel de temporada está mais barato entre TemporadaLivre, OLX e proprietários diretos.
          </p>
        </div>

        {/* Formulário Central de Busca */}
        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-200 p-3 sm:p-4 max-w-5xl mx-auto"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-3 items-center">
            {/* Campo Cidade */}
            <div className="lg:col-span-4 relative">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
                Destino / Cidade
              </label>
              <div className="relative flex items-center">
                <MapPin className="absolute left-3 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  value={filters.city}
                  onChange={(e) => setFilters({ ...filters, city: e.target.value })}
                  placeholder="Ex: Atibaia, Ibiúna..."
                  required
                  className="w-full pl-9 pr-3 py-2 text-sm font-semibold bg-slate-50 hover:bg-slate-100/80 focus:bg-white rounded-xl border border-slate-200 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 outline-none transition-all"
                />
              </div>
            </div>

            {/* Check-in */}
            <div className="lg:col-span-2 relative">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
                Check-in
              </label>
              <div className="relative flex items-center">
                <Calendar className="absolute left-3 h-4 w-4 text-slate-400" />
                <input
                  type="date"
                  value={filters.check_in || ''}
                  onChange={(e) => setFilters({ ...filters, check_in: e.target.value })}
                  className="w-full pl-9 pr-2 py-2 text-xs font-semibold bg-slate-50 hover:bg-slate-100/80 focus:bg-white rounded-xl border border-slate-200 focus:border-brand-500 outline-none transition-all"
                />
              </div>
            </div>

            {/* Check-out */}
            <div className="lg:col-span-2 relative">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
                Check-out
              </label>
              <div className="relative flex items-center">
                <Calendar className="absolute left-3 h-4 w-4 text-slate-400" />
                <input
                  type="date"
                  value={filters.check_out || ''}
                  onChange={(e) => setFilters({ ...filters, check_out: e.target.value })}
                  className="w-full pl-9 pr-2 py-2 text-xs font-semibold bg-slate-50 hover:bg-slate-100/80 focus:bg-white rounded-xl border border-slate-200 focus:border-brand-500 outline-none transition-all"
                />
              </div>
            </div>

            {/* Hóspedes */}
            <div className="lg:col-span-2 relative">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
                Hóspedes
              </label>
              <div className="relative flex items-center">
                <Users className="absolute left-3 h-4 w-4 text-slate-400" />
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={filters.guests}
                  onChange={(e) => setFilters({ ...filters, guests: parseInt(e.target.value) || 1 })}
                  className="w-full pl-9 pr-2 py-2 text-xs font-semibold bg-slate-50 hover:bg-slate-100/80 focus:bg-white rounded-xl border border-slate-200 focus:border-brand-500 outline-none transition-all"
                />
              </div>
            </div>

            {/* Botão de Busca */}
            <div className="lg:col-span-2 flex items-end">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full mt-5 lg:mt-0 py-2.5 px-4 bg-brand-600 hover:bg-brand-700 text-white font-bold rounded-xl shadow-md shadow-brand-600/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                {isLoading ? (
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
                <span>Buscar</span>
              </button>
            </div>
          </div>

          {/* Atalhos de Cidades e Tipos */}
          <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-slate-400 font-medium">Cidades populares:</span>
              {quickCities.map((c) => (
                <button
                  key={c}
                  type="button"
                  onClick={() => {
                    setFilters({ ...filters, city: c });
                  }}
                  className={`px-2 py-1 rounded-md font-medium transition-colors ${
                    filters.city.toLowerCase() === c.toLowerCase()
                      ? 'bg-brand-100 text-brand-800'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg">
              {['todos', 'chacara', 'sitio', 'casa'].map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setFilters({ ...filters, property_type: type })}
                  className={`px-2.5 py-1 rounded-md text-xs font-semibold capitalize transition-all ${
                    filters.property_type === type
                      ? 'bg-white text-slate-900 shadow-xs'
                      : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  {type === 'todos' ? 'Todos os Tipos' : type}
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
