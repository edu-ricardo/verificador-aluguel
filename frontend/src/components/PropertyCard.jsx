import React, { useState } from 'react';
import {
  Users,
  BedDouble,
  Bath,
  Waves,
  Dog,
  ExternalLink,
  Sparkles,
  TrendingDown,
  Info,
  CheckCircle2,
} from 'lucide-react';

export default function PropertyCard({ property, nights, onOpenDetails }) {
  const [currentImgIdx, setCurrentImgIdx] = useState(0);
  const images = property.images && property.images.length > 0 ? property.images : [
    'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80'
  ];

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(val);
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs hover:shadow-md transition-all flex flex-col md:flex-row group">
      {/* Imagem */}
      <div className="relative md:w-80 h-56 md:h-auto shrink-0 bg-slate-100 overflow-hidden">
        <img
          src={images[currentImgIdx]}
          alt={property.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          onError={(e) => {
            e.target.src = 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80';
          }}
        />

        {/* Badge do Tipo de Imóvel */}
        <div className="absolute top-3 left-3 bg-slate-900/80 backdrop-blur-xs text-white text-[11px] font-bold px-2.5 py-1 rounded-full capitalize">
          {property.property_type}
        </div>

        {/* Badge de Economia se houver mais de uma plataforma */}
        {property.max_savings > 0 && (
          <div className="absolute bottom-3 left-3 right-3 bg-emerald-600/95 backdrop-blur-xs text-white text-xs font-bold px-3 py-1.5 rounded-xl shadow-lg flex items-center gap-1.5">
            <TrendingDown className="h-4 w-4" />
            <span>Economize {formatCurrency(property.max_savings)} na melhor oferta!</span>
          </div>
        )}
      </div>

      {/* Conteúdo Principal */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        <div>
          {/* Localização & Título */}
          <div className="flex items-center justify-between gap-2 mb-1">
            <span className="text-xs font-semibold text-slate-500">
              {property.neighborhood ? `${property.neighborhood}, ` : ''}{property.city} - {property.state}
            </span>
            {property.platforms.length > 1 && (
              <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full border border-indigo-200">
                {property.platforms.length} portais comparados
              </span>
            )}
          </div>

          <h3 className="text-base font-bold text-slate-900 line-clamp-2 hover:text-brand-700 transition-colors">
            {property.title}
          </h3>

          {/* Características */}
          <div className="flex flex-wrap items-center gap-3 mt-3 text-xs text-slate-600">
            <div className="flex items-center gap-1">
              <Users className="h-3.5 w-3.5 text-slate-400" />
              <span>Até {property.max_guests} pessoas</span>
            </div>
            <div className="flex items-center gap-1">
              <BedDouble className="h-3.5 w-3.5 text-slate-400" />
              <span>{property.bedrooms} quartos</span>
            </div>
            <div className="flex items-center gap-1">
              <Bath className="h-3.5 w-3.5 text-slate-400" />
              <span>{property.bathrooms} banheiros</span>
            </div>
            {property.has_pool && (
              <div className="flex items-center gap-1 text-sky-600 font-medium">
                <Waves className="h-3.5 w-3.5" />
                <span>Piscina</span>
              </div>
            )}
            {property.allows_pets && (
              <div className="flex items-center gap-1 text-amber-600 font-medium">
                <Dog className="h-3.5 w-3.5" />
                <span>Pet friendly</span>
              </div>
            )}
          </div>
        </div>

        {/* Comparador de Preços por Plataforma */}
        <div className="mt-4 pt-4 border-t border-slate-100">
          <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
            <span>Comparativo de Valores ({nights} noites)</span>
            <span className="text-slate-400 font-normal">Diária + Limpeza + Taxas</span>
          </div>

          <div className="space-y-2">
            {property.platforms.map((plat) => (
              <div
                key={plat.external_id + plat.platform}
                className={`flex items-center justify-between p-2.5 rounded-xl border text-xs transition-all ${
                  plat.is_cheapest
                    ? 'bg-emerald-50/70 border-emerald-300 ring-1 ring-emerald-500/20'
                    : 'bg-slate-50/60 border-slate-200'
                }`}
              >
                <div className="flex items-center gap-2">
                  {plat.is_cheapest && (
                    <span className="bg-emerald-600 text-white text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded-md flex items-center gap-0.5">
                      <Sparkles className="h-2.5 w-2.5" /> Menor Preço
                    </span>
                  )}
                  <span className="font-bold text-slate-800">{plat.platform_name}</span>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="text-[11px] text-slate-500 block">
                      {formatCurrency(plat.daily_rate)}/noite
                    </span>
                    <span className={`font-black text-sm ${plat.is_cheapest ? 'text-emerald-700' : 'text-slate-900'}`}>
                      {formatCurrency(plat.total_price)} <span className="text-[10px] font-medium text-slate-400">total</span>
                    </span>
                  </div>

                  <a
                    href={plat.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`p-2 rounded-lg font-bold flex items-center gap-1 transition-all ${
                      plat.is_cheapest
                        ? 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs'
                        : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200'
                    }`}
                    title={`Abrir anúncio no ${plat.platform_name}`}
                  >
                    <span className="hidden sm:inline text-[11px]">Ver Oferta</span>
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
