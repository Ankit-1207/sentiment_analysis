import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { 
  FiInstagram as Instagram, FiSearch as Search, 
  FiShield as ShieldAlert, FiCheckCircle as ShieldCheck,
  FiActivity as Activity, FiUsers as Users, 
  FiAlertTriangle as AlertTriangle, FiAlertCircle as AlertCircle, 
  FiPlayCircle as PlayCircle, FiLoader as Loader2
} from 'react-icons/fi';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, Legend
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

const App = () => {
  // Config & State
  const [apifyToken, setApifyToken] = useState('');
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState('idle'); // idle, loading, streaming, finished
  const [error, setError] = useState(null);
  
  // Data streams
  const [buffer, setBuffer] = useState([]);
  const [liveFeed, setLiveFeed] = useState([]);
  const [pointer, setPointer] = useState(0);

  // Filters
  const [searchEntry, setSearchEntry] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('all');

  // --- Real-Time Streaming Simulation ---
  useEffect(() => {
    if (status !== 'streaming') return;
    
    // Push 1 comment every 2.5 seconds to simulate live feed
    const interval = setInterval(() => {
      if (pointer < buffer.length) {
        setLiveFeed(prev => [buffer[pointer], ...prev]);
        setPointer(p => p + 1);
      } else {
        setStatus('finished');
        clearInterval(interval);
      }
    }, 2500);
    
    return () => clearInterval(interval);
  }, [status, pointer, buffer]);

  // --- API Call ---
  const startMonitoring = async (e) => {
    e.preventDefault();
    if (!apifyToken || !url) return;
    
    setStatus('loading');
    setError(null);
    setBuffer([]);
    setLiveFeed([]);
    setPointer(0);

    try {
      const res = await axios.post('http://127.0.0.1:5000/api/analyze', {
        apifyToken, url
      });
      // Set the incoming comments buffer and kick off streaming
      setBuffer(res.data.comments || []);
      setStatus('streaming');
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "Failed to start monitoring server.");
      setStatus('idle');
    }
  };

  // --- Derived Statistics ---
  const stats = useMemo(() => {
    let positive = 0, negative = 0, neutral = 0, abusive = 0;
    liveFeed.forEach(c => {
      if (c.sentiment === 'positive') positive++;
      else if (c.sentiment === 'negative') negative++;
      else if (c.sentiment === 'abusive') abusive++;
      else neutral++;
    });
    return { total: liveFeed.length, positive, negative, neutral, abusive };
  }, [liveFeed]);

  const userStats = useMemo(() => {
    const map = {};
    liveFeed.forEach(c => {
      if (!map[c.username]) map[c.username] = { total: 0, toxic: 0 };
      map[c.username].total++;
      if (c.sentiment === 'negative' || c.sentiment === 'abusive') {
        map[c.username].toxic++;
      }
    });
    
    let flagged = 0;
    let banned = 0;
    const usersList = Object.keys(map).map(username => {
      const u = map[username];
      const toxicPercent = (u.toxic / u.total) * 100;
      let statusStr = "Safe";
      
      if (toxicPercent >= 60) { statusStr = "Ban"; banned++; flagged++; }
      else if (toxicPercent >= 30) { statusStr = "Warning"; flagged++; }

      return { username, total: u.total, toxicPercent, status: statusStr };
    }).sort((a,b) => b.toxicPercent - a.toxicPercent);

    return { list: usersList, flagged, banned };
  }, [liveFeed]);

  // --- Filtering ---
  const filteredFeed = liveFeed.filter(c => {
    if (sentimentFilter !== 'all' && c.sentiment !== sentimentFilter) return false;
    if (searchEntry && !c.username.toLowerCase().includes(searchEntry.toLowerCase()) && !c.text.toLowerCase().includes(searchEntry.toLowerCase())) return false;
    return true;
  });

  // --- Chart Data ---
  const sentimentChartData = [
    { name: 'Positive', value: stats.positive, color: '#22c55e' },
    { name: 'Neutral', value: stats.neutral, color: '#9ca3af' },
    { name: 'Negative', value: stats.negative, color: '#f97316' },
    { name: 'Abusive', value: stats.abusive, color: '#ef4444' }
  ];

  const toxicityPieData = [
    { name: 'Toxic', value: stats.negative + stats.abusive, color: '#ef4444' },
    { name: 'Safe', value: stats.positive + stats.neutral, color: '#22c55e' }
  ];

  return (
    <div className="min-h-screen p-4 lg:p-8">
      {/* HEADER */}
      <header className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-tr from-instagram-start via-instagram-mid2 to-instagram-end rounded-xl shadow-lg">
            <Instagram className="text-white w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
              TrustNTrack Live
            </h1>
            <p className="text-dark-muted text-sm">Real-Time Moderation Dashboard</p>
          </div>
        </div>

        {/* Control Panel */}
        <form onSubmit={startMonitoring} className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          <input 
            className="input-modern w-48" 
            placeholder="Apify Token" 
            type="password"
            value={apifyToken} onChange={e => setApifyToken(e.target.value)} required
          />
          <input 
            className="input-modern w-64" 
            placeholder="Instagram Post URL" 
            type="url"
            value={url} onChange={e => setUrl(e.target.value)} required 
          />
          <button type="submit" className="btn-ig px-6 py-2 flex items-center justify-center gap-2" disabled={status === 'loading' || status === 'streaming'}>
            {status === 'loading' ? <Loader2 className="animate-spin w-5 h-5" /> : <PlayCircle className="w-5 h-5" />}
            {status === 'streaming' ? 'Monitoring...' : status === 'loading' ? 'Connecting...' : 'Start Feed'}
          </button>
        </form>
      </header>

      {error && (
        <div className="mb-6 p-4 bg-red-900/40 border border-red-500/50 rounded-lg flex items-center gap-3 text-red-200">
          <AlertCircle /> <p>{error}</p>
        </div>
      )}

      {/* OVERVIEW CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {[
          { label: "Analyzed", val: stats.total, color: "text-blue-400" },
          { label: "Positive", val: stats.positive, color: "text-green-400" },
          { label: "Negative", val: stats.negative, color: "text-orange-400" },
          { label: "Abusive", val: stats.abusive, color: "text-red-500" },
          { label: "Flagged Users", val: userStats.flagged, color: "text-yellow-400" },
          { label: "Banned Users", val: userStats.banned, color: "text-red-500" }
        ].map((card, idx) => (
          <div key={idx} className="glass-panel p-4 flex flex-col items-center justify-center">
            <span className="text-dark-muted text-sm font-medium">{card.label}</span>
            <span className={`text-3xl font-bold mt-1 ${card.color}`}>
               {card.val}
            </span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* LEFT COMPONENT: LIVE FEED */}
        <div className="lg:col-span-2 flex flex-col gap-8">
          
          <div className="glass-panel p-6 h-[500px] flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Activity className={status === 'streaming' ? "text-green-400 animate-pulse" : "text-gray-500"} />
                Live Comment Stream
              </h2>
              
              <div className="flex gap-3">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
                  <input 
                    placeholder="Search feed..." 
                    className="input-modern pl-9 py-1.5 text-sm"
                    value={searchEntry} onChange={e => setSearchEntry(e.target.value)}
                  />
                </div>
                <select 
                  className="input-modern py-1.5 text-sm"
                  value={sentimentFilter} onChange={e => setSentimentFilter(e.target.value)}
                >
                  <option value="all">All Sentiments</option>
                  <option value="abusive">Abusive Only</option>
                  <option value="negative">Negative</option>
                </select>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 flex flex-col gap-3">
              <AnimatePresence>
                {filteredFeed.map((comment, idx) => (
                  <motion.div 
                    key={comment.text + idx} // using idx allows duplicates in mock feed
                    initial={{ opacity: 0, x: -20, height: 0 }}
                    animate={{ opacity: 1, x: 0, height: 'auto' }}
                    className="p-4 bg-dark-bg/50 border border-dark-border rounded-lg"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center font-bold text-xs">
                          {comment.username.substring(0,2).toUpperCase()}
                        </div>
                        <div>
                          <p className="font-semibold text-sm">@{comment.username}</p>
                          <p className="text-xs text-gray-500">{comment.timestamp || "Just now"}</p>
                        </div>
                      </div>
                      <span className={`badge badge-${comment.sentiment}`}>
                        {comment.sentiment.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300">{comment.text}</p>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {status === 'idle' && liveFeed.length === 0 && (
                <div className="text-center text-gray-500 mt-20">
                  <Activity className="w-12 h-12 mx-auto mb-4 opacity-20" />
                  Enter a URL and click Start Feed to monitor comments in real-time.
                </div>
              )}
            </div>
          </div>

          {/* BOTTOM CHARTS */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="glass-panel p-6 h-[300px]">
              <h3 className="font-semibold mb-4 text-gray-300">Sentiment Distribution</h3>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sentimentChartData}>
                  <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                  <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} contentStyle={{backgroundColor: '#1e1e1e', borderColor: '#333'}}/>
                  <Bar dataKey="value" radius={[4,4,0,0]}>
                    {sentimentChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            <div className="glass-panel p-6 h-[300px]">
              <h3 className="font-semibold mb-4 text-gray-300">Overall Toxicity Risk</h3>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={toxicityPieData}
                    cx="50%" cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {toxicityPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{backgroundColor: '#1e1e1e', borderColor: '#333'}}/>
                  <Legend verticalAlign="bottom" height={36}/>
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          
        </div>

        {/* RIGHT COMPONENT: FLAGGED USERS */}
        <div className="glass-panel p-6 h-[832px] flex flex-col">
          <div className="flex items-center gap-2 mb-6">
            <Users className="text-gray-400" />
            <h2 className="text-xl font-bold">User Risk Profiles</h2>
          </div>
          
          <div className="flex-1 overflow-y-auto pr-2 space-y-3">
            {userStats.list.length === 0 && (
               <div className="text-center text-gray-500 mt-10">No user data available.</div>
            )}
            
            <AnimatePresence>
              {userStats.list.map(user => (
                <motion.div 
                  key={user.username}
                  layout
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className={`p-3 rounded-lg border ${
                    user.status === 'Ban' ? 'bg-red-900/20 border-red-500/50' :
                    user.status === 'Warning' ? 'bg-yellow-900/20 border-yellow-500/50' :
                    'bg-dark-bg border-dark-border'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-sm">@{user.username}</span>
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                      user.status === 'Ban' ? 'bg-red-500 text-white' :
                      user.status === 'Warning' ? 'bg-yellow-500 text-black' :
                      'bg-green-500 text-white'
                    }`}>
                      {user.status}
                    </span>
                  </div>
                  
                  <div className="mt-2 flex justify-between text-xs text-gray-400">
                    <span>Comments: {user.total}</span>
                    <span className={user.status !== 'Safe' ? (user.status === 'Ban' ? 'text-red-400' : 'text-yellow-400') : ''}>
                      {user.toxicPercent.toFixed(0)}% Toxic
                    </span>
                  </div>
                  
                  {/* Progress bar */}
                  <div className="w-full bg-gray-800 h-1.5 mt-2 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${
                        user.status === 'Ban' ? 'bg-red-500' :
                        user.status === 'Warning' ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${user.toxicPercent}%` }}
                    />
                  </div>
                  
                  {user.status === 'Ban' && (
                    <div className="mt-2 text-xs text-red-400 flex items-center gap-1">
                      <ShieldAlert className="w-3 h-3" /> Recommend banning user
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>

      </div>
    </div>
  );
};

export default App;
