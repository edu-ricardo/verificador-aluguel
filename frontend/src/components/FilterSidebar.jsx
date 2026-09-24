import React from 'react';
import { SlidersHorizontal, Waves, Dog, Flame, ArrowUpDown } from 'lucide-react';

export default function FilterSidebar({ filters, setFilters }) {
  return (
    <aside className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-6">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-brand-600" />
          <h3 className="font-bold text-slate-900 text-sm">Filtros Refinados</h3>
        </div>
        <button
          onClick={() =>
            setFilters({
              ...filters,
              has_pool: false,
              allows_pets: false,
              min_price: '',
              max_price: '',
              platforms: [],
              sort_by: 'price_asc',
            })
          }
          className="text-xs text-brand-600 hover:text-brand-800 font-medium"
        >
          Limpar
        </button>
      </div>

      {/* Ordenação */}
      <div>
        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
          Ordenar Por
        </label>
        <div className="relative">
          <select
            value={filters.sort_by}
            onChange={(e) => setFilters({ ...filters, sort_by: e.target.value })}
            className="w-full text-xs font-semibold bg-slate-50 border border-slate-200 rounded-xl p-2.5 outline-none focus:border-brand-500 text-slate-700"
          >
            <option value="price_asc">Menor Preço Total (Diárias + Taxas)</option>
            <option value="savings_desc">Maior Economia Entre Portais</option>
            <option value="price_desc">Maior Preço</option>
            <option value="guests_desc">Capacidade de Hóspedes (Maior)</option>
          </select>
        </div>
      </div>

      {/* Faixa de Preço */}
      <div>
        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
          Preço da Diária (R$)
        </label>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <span className="text-[10px] text-slate-400 font-semibold">Mínimo</span>
            <input
              type="number"
              placeholder="R$ 0"
              value={filters.min_price || ''}
              onChange={(e) => setFilters({ ...filters, min_price: e.target.value })}
              className="w-full text-xs font-semibold p-2 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-brand-500"
            />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 font-semibold">Máximo</span>
            <input
              type="number"
              placeholder="R$ 3.000"
              value={filters.max_price || ''}
              onChange={(e) => setFilters({ ...filters, max_price: e.target.value })}
              className="w-full text-xs font-semibold p-2 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-brand-500"
            />
          </div>
        </div>
      </div>

      {/* Comodidades Obrigatórias */}
      <div>
        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
          Comodidades
        </label>
        <div className="space-y-2">
          <label className="flex items-center gap-2.5 text-xs font-medium text-slate-700 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={filters.has_pool}
              onChange={(e) => setFilters({ ...filters, has_pool: e.target.checked })}
              className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300"
            />
            <Waves className="h-3.5 w-3.5 text-sky-500" />
            <span>Com Piscina</span>
          </label>

          <label className="flex items-center gap-2.5 text-xs font-medium text-slate-700 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={filters.allows_pets}
              onChange={(e) => setFilters({ ...filters, allows_pets: e.target.checked })}
              className="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300"
            />
            <Dog className="h-3.5 w-3.5 text-amber-600" />
            <span>Aceita Animais (Pet Friendly)</span>
          </label>
        </div>
      </div>

      {/* Portais Ativos */}
      <div>
        <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
          Portais Comparados
        </label>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-700 bg-slate-50 p-2 rounded-lg border border-slate-100">
            <span className="font-semibold text-blue-600">TemporadaLivre</span>
            <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full font-bold">Ativo</span>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-700 bg-slate-50 p-2 rounded-lg border border-slate-100">
            <span className="font-semibold text-purple-600">OLX Imóveis</span>
            <span className="text-[10px] bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded-full font-bold">Ativo</span>
          </div>
          <div className="flex items-center justify-between text-xs text-slate-400 bg-slate-50/50 p-2 rounded-lg border border-slate-100">
            <span className="font-medium">Airbnb & Booking</span>
            <span className="text-[10px] bg-slate-200 text-slate-500 px-1.5 py-0.5 rounded-full font-semibold">Em breve</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
