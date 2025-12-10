// services/dashboard-frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';

const CURRENCY_API = import.meta.env.VITE_CURRENCY_API_URL || 'http://localhost:8001/api/v1';
const DJANGO_API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export default function DashboardApp() {
  const [currencies, setCurrencies] = useState([]);
  const [historicalData, setHistoricalData] = useState({});
  const [selectedCurrency, setSelectedCurrency] = useState('CLP');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [timeRange, setTimeRange] = useState(30);

  // Cargar resumen de dashboard
  useEffect(() => {
    fetchDashboardSummary();
    const interval = setInterval(fetchDashboardSummary, 300000); // Cada 5 min
    return () => clearInterval(interval);
  }, []);

  // Cargar datos históricos
  useEffect(() => {
    if (selectedCurrency) {
      fetchHistoricalData(selectedCurrency, timeRange);
    }
  }, [selectedCurrency, timeRange]);

  const fetchDashboardSummary = async () => {
    try {
      const response = await fetch(`${CURRENCY_API}/dashboard/summary`);
      const data = await response.json();
      setCurrencies(data.currencies || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
      setLoading(false);
    }
  };

  const fetchHistoricalData = async (currency, days) => {
    try {
      const response = await fetch(
        `${CURRENCY_API}/rates/history/${currency}?base=USD&days=${days}`
      );
      const data = await response.json();
      setHistoricalData(prev => ({
        ...prev,
        [currency]: data
      }));
    } catch (error) {
      console.error('Error fetching historical:', error);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-CL', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CL', { month: 'short', day: 'numeric' });
  };

  // Card de Moneda
  const CurrencyCard = ({ data }) => {
    const trend = data.change_percent || 0;
    const isPositive = trend >= 0;

    return (
      <div className="bg-gray-800 rounded-lg p-6 shadow-lg hover:shadow-xl transition-shadow">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-gray-400 text-sm font-medium">
              USD/{data.currency}
            </h3>
            <p className="text-3xl font-bold text-white mt-1">
              {formatCurrency(data.current_rate)}
            </p>
          </div>
          <div className={`p-2 rounded-full ${isPositive ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
            {isPositive ? (
              <TrendingUp className="w-6 h-6 text-green-500" />
            ) : (
              <TrendingDown className="w-6 h-6 text-red-500" />
            )}
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Promedio 30d:</span>
            <span className="text-gray-200">{formatCurrency(data.avg_30d || 0)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Máximo:</span>
            <span className="text-green-400">{formatCurrency(data.max_30d || 0)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-400">Mínimo:</span>
            <span className="text-red-400">{formatCurrency(data.min_30d || 0)}</span>
          </div>
        </div>

        <div className={`mt-4 pt-4 border-t border-gray-700 flex items-center justify-between`}>
          <span className="text-sm text-gray-400">Cambio 30d:</span>
          <span className={`text-sm font-semibold ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
            {isPositive ? '+' : ''}{trend.toFixed(2)}%
          </span>
        </div>
      </div>
    );
  };

  // Gráfico Principal
  const MainChart = () => {
    const data = historicalData[selectedCurrency] || [];
    const chartData = data.map(item => ({
      date: formatDate(item.date),
      value: parseFloat(item.rate)
    }));

    return (
      <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white">
              Histórico USD/{selectedCurrency}
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              Últimos {timeRange} días
            </p>
          </div>

          <div className="flex gap-4 mt-4 md:mt-0">
            <select
              value={selectedCurrency}
              onChange={(e) => setSelectedCurrency(e.target.value)}
              className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:border-blue-500"
            >
              <option value="CLP">CLP (Peso Chileno)</option>
              <option value="COP">COP (Peso Colombiano)</option>
              <option value="PEN">PEN (Sol Peruano)</option>
              <option value="MXN">MXN (Peso Mexicano)</option>
              <option value="EUR">EUR (Euro)</option>
            </select>

            <div className="flex gap-2">
              {[7, 30, 90, 180].map(days => (
                <button
                  key={days}
                  onClick={() => setTimeRange(days)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    timeRange === days
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {days}d
                </button>
              ))}
            </div>
          </div>
        </div>

        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => value.toFixed(2)}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#fff'
              }}
              formatter={(value) => [formatCurrency(value), 'Tasa']}
            />
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke="#3b82f6" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorValue)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    );
  };

  // Gráfico Comparativo
  const ComparisonChart = () => {
    const compareCurrencies = ['CLP', 'COP', 'PEN'];
    const colors = ['#3b82f6', '#10b981', '#f59e0b'];

    // Normalizar datos para comparación
    const normalizedData = {};
    compareCurrencies.forEach(curr => {
      const data = historicalData[curr] || [];
      data.forEach(item => {
        const date = formatDate(item.date);
        if (!normalizedData[date]) normalizedData[date] = { date };
        normalizedData[date][curr] = parseFloat(item.rate);
      });
    });

    const chartData = Object.values(normalizedData);

    return (
      <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
        <h2 className="text-2xl font-bold text-white mb-6">
          Comparación de Monedas Latinoamericanas
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <Legend />
            {compareCurrencies.map((curr, idx) => (
              <Line
                key={curr}
                type="monotone"
                dataKey={curr}
                stroke={colors[idx]}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-400">Cargando datos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">NUAM Dashboard</h1>
              <p className="text-blue-100 mt-1">
                Sistema de Monitoreo de Divisas y Operaciones
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2">
                <p className="text-xs text-blue-100">Última actualización</p>
                <p className="text-sm font-semibold text-white">
                  {new Date().toLocaleTimeString('es-CL')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Currency Cards Grid */}
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">
            Valores Actuales
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {currencies.map((currency) => (
              <CurrencyCard key={currency.currency} data={currency} />
            ))}
          </div>
        </section>

        {/* Main Chart */}
        <section className="mb-8">
          <MainChart />
        </section>

        {/* Comparison Chart */}
        <section className="mb-8">
          <ComparisonChart />
        </section>

        {/* Stats Cards */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Operaciones Hoy</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {stats?.operaciones_hoy || 0}
                </p>
              </div>
              <div className="bg-blue-500/20 p-3 rounded-full">
                <Activity className="w-8 h-8 text-blue-500" />
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total Operaciones</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {stats?.total_operaciones || 0}
                </p>
              </div>
              <div className="bg-green-500/20 p-3 rounded-full">
                <DollarSign className="w-8 h-8 text-green-500" />
              </div>
            </div>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Usuarios Activos</p>
                <p className="text-3xl font-bold text-white mt-2">
                  {stats?.usuarios_activos || 0}
                </p>
              </div>
              <div className="bg-purple-500/20 p-3 rounded-full">
                <Activity className="w-8 h-8 text-purple-500" />
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-gray-400 text-sm">
            <p>© 2024 NUAM - Sistema de Gestión de Operaciones Financieras</p>
            <p className="mt-1">
              Desarrollado con React, FastAPI y Django
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}