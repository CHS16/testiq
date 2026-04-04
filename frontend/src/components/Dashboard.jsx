import React, { useState, useEffect } from 'react';
import { getInteractions, getInteractionById } from '../services/api';
import { Phone, AlertTriangle, ShieldAlert, Briefcase, Search, Activity, ChevronRight, X } from 'lucide-react';

const Dashboard = () => {
  const [interactions, setInteractions] = useState([]);
  const [filteredInteractions, setFilteredInteractions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Selection state
  const [selectedInteraction, setSelectedInteraction] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsError, setDetailsError] = useState(null);

  // Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [intentFilter, setIntentFilter] = useState('');
  const [urgencyFilter, setUrgencyFilter] = useState(''); // 'high', 'medium', 'low'

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await getInteractions();
      setInteractions(data);
      setFilteredInteractions(data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch interactions. Ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let result = interactions;

    if (searchTerm) {
      const lowerSearch = searchTerm.toLowerCase();
      result = result.filter(i => 
        (i.callerName && i.callerName.toLowerCase().includes(lowerSearch)) ||
        (i.callerNumber && i.callerNumber.toLowerCase().includes(lowerSearch))
      );
    }

    if (intentFilter) {
      result = result.filter(i => i.intent.toLowerCase() === intentFilter.toLowerCase());
    }

    if (urgencyFilter) {
      if (urgencyFilter === 'high') result = result.filter(i => i.urgency_score >= 8);
      else if (urgencyFilter === 'medium') result = result.filter(i => i.urgency_score >= 4 && i.urgency_score <= 7);
      else if (urgencyFilter === 'low') result = result.filter(i => i.urgency_score <= 3);
    }

    setFilteredInteractions(result);
  }, [searchTerm, intentFilter, urgencyFilter, interactions]);

  const handleRowClick = async (id) => {
    setDetailsLoading(true);
    setDetailsError(null);
    try {
      const data = await getInteractionById(id);
      setSelectedInteraction(data);
    } catch (err) {
      setDetailsError('Failed to fetch interaction details.');
    } finally {
      setDetailsLoading(false);
    }
  };

  const getUrgencyBadge = (score) => {
    if (score >= 8) return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">{score} - Critical</span>;
    if (score >= 4) return <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-700 rounded-full">{score} - Medium</span>;
    return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded-full">{score} - Low</span>;
  };

  const getIntentBadge = (intent) => {
    const i = intent.toLowerCase();
    if (i.includes('spam')) return <span className="px-3 py-1 text-xs font-semibold bg-red-50 text-red-600 rounded-lg border border-red-200">{intent}</span>;
    if (i.includes('support')) return <span className="px-3 py-1 text-xs font-semibold bg-green-50 text-green-600 rounded-lg border border-green-200">{intent}</span>;
    if (i.includes('sales')) return <span className="px-3 py-1 text-xs font-semibold bg-blue-50 text-blue-600 rounded-lg border border-blue-200">{intent}</span>;
    if (i.includes('urgent')) return <span className="px-3 py-1 text-xs font-semibold bg-orange-50 text-orange-600 rounded-lg border border-orange-200">{intent}</span>;
    return <span className="px-3 py-1 text-xs font-semibold bg-gray-100 text-gray-700 rounded-lg border border-gray-200">{intent}</span>;
  };

  const stats = {
    total: interactions.length,
    urgent: interactions.filter(i => i.urgency_score >= 8).length,
    spam: interactions.filter(i => i.spam_confidence >= 70).length,
    active: interactions.filter(i => i.resolution_status !== 'Resolved by AI' && i.resolution_status !== 'Rejected as Spam').length
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <div className={`flex-1 flex flex-col overflow-y-auto w-full transition-all duration-300 ${selectedInteraction ? 'lg:w-2/3 lg:pr-[400px]' : ''}`}>
        
        {/* Header Content */}
        <div className="bg-white px-8 py-6 border-b border-gray-200 sticky top-0 z-10 shadow-sm">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <Activity className="text-primary w-6 h-6" />
                IntentIQ Dashboard
              </h1>
              <p className="text-gray-500 text-sm mt-1">Live interaction monitoring & AI call analytics</p>
            </div>
            <button onClick={fetchData} className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition-colors shadow-sm">
              Refresh Data
            </button>
          </div>

          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center gap-4">
              <div className="bg-blue-50 p-3 rounded-lg"><Phone className="text-blue-500 w-5 h-5" /></div>
              <div>
                <p className="text-xs text-gray-500 font-medium">Total Calls</p>
                <p className="text-xl font-bold text-gray-900">{stats.total}</p>
              </div>
            </div>
             <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center gap-4">
              <div className="bg-red-50 p-3 rounded-lg"><AlertTriangle className="text-red-500 w-5 h-5" /></div>
              <div>
                <p className="text-xs text-gray-500 font-medium">Urgent Issues</p>
                <p className="text-xl font-bold text-gray-900">{stats.urgent}</p>
              </div>
            </div>
            <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center gap-4">
              <div className="bg-orange-50 p-3 rounded-lg"><ShieldAlert className="text-orange-500 w-5 h-5" /></div>
              <div>
                <p className="text-xs text-gray-500 font-medium">Spam Detected</p>
                <p className="text-xl font-bold text-gray-900">{stats.spam}</p>
              </div>
            </div>
            <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center gap-4">
              <div className="bg-purple-50 p-3 rounded-lg"><Briefcase className="text-purple-500 w-5 h-5" /></div>
              <div>
                <p className="text-xs text-gray-500 font-medium">Active Cases</p>
                <p className="text-xl font-bold text-gray-900">{stats.active}</p>
              </div>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-4 items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name or number..."
                className="w-full pl-9 pr-4 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <select
              className="border border-gray-200 rounded-lg px-4 py-2 text-sm bg-white outline-none focus:border-primary"
              value={intentFilter}
              onChange={(e) => setIntentFilter(e.target.value)}
            >
              <option value="">All Intents</option>
              <option value="Sales">Sales</option>
              <option value="Support">Support</option>
              <option value="Spam">Spam</option>
            </select>
            <select
              className="border border-gray-200 rounded-lg px-4 py-2 text-sm bg-white outline-none focus:border-primary"
              value={urgencyFilter}
              onChange={(e) => setUrgencyFilter(e.target.value)}
            >
              <option value="">All Urgency</option>
              <option value="high">High (8-10)</option>
              <option value="medium">Medium (4-7)</option>
              <option value="low">Low (1-3)</option>
            </select>
          </div>
        </div>

        {/* Table Content */}
        <div className="p-8">
          {error ? (
             <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center gap-2">
               <AlertTriangle className="w-5 h-5" />
               {error}
             </div>
          ) : loading ? (
            <div className="flex justify-center items-center py-20">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : filteredInteractions.length === 0 ? (
            <div className="text-center py-20 text-gray-500">
              <p>No interactions found matching your criteria.</p>
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-100 text-xs uppercase text-gray-500 font-semibold tracking-wider">
                    <th className="px-6 py-4">Caller</th>
                    <th className="px-6 py-4">Intent</th>
                    <th className="px-6 py-4">Urgency</th>
                    <th className="px-6 py-4">Sentiment</th>
                    <th className="px-6 py-4">Summary</th>
                    <th className="px-6 py-4">Time</th>
                    <th className="px-6 py-4"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-sm">
                  {filteredInteractions.map(interaction => {
                    const isSpam = interaction.spam_confidence >= 70;
                    return (
                      <tr 
                        key={interaction.id} 
                        onClick={() => handleRowClick(interaction.id)}
                        className={`hover:bg-blue-50/50 cursor-pointer transition-colors ${selectedInteraction?.id === interaction.id ? 'bg-blue-50/50' : ''}`}
                      >
                        <td className="px-6 py-4">
                          <div className="font-medium text-gray-900">{interaction.callerName || 'Unknown'}</div>
                          <div className="text-xs text-gray-500">{interaction.callerNumber || 'N/A'}</div>
                          {isSpam && <span className="inline-block mt-1 px-2 py-0.5 text-[10px] bg-red-100 text-red-600 rounded">Spam User</span>}
                        </td>
                        <td className="px-6 py-4">
                          {getIntentBadge(interaction.intent)}
                        </td>
                        <td className="px-6 py-4">
                          {getUrgencyBadge(interaction.urgency_score)}
                        </td>
                        <td className="px-6 py-4 font-medium text-gray-600">
                          {interaction.sentiment}
                        </td>
                        <td className="px-6 py-4 text-gray-600 max-w-[200px] truncate">
                          {interaction.summary}
                        </td>
                        <td className="px-6 py-4 text-gray-400 text-xs whitespace-nowrap">
                          {new Date(interaction.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-gray-400">
                          <ChevronRight className="w-4 h-4 ml-auto" />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Details Side Panel */}
      {selectedInteraction && (
        <div className="fixed inset-y-0 right-0 w-full lg:w-[400px] bg-white shadow-2xl border-l border-gray-200 flex flex-col z-20 animate-in slide-in-from-right duration-300">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 bg-gray-50">
            <h2 className="font-semibold text-gray-900">Interaction Details</h2>
            <button onClick={() => setSelectedInteraction(null)} className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-200/50 transition-colors">
              <X className="w-4 h-4" />
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-6">
            {detailsLoading ? (
               <div className="flex justify-center items-center py-20">
                 <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
               </div>
            ) : detailsError ? (
               <div className="text-red-500 text-sm text-center py-10">{detailsError}</div>
            ) : (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{selectedInteraction.callerName || 'Unknown Caller'}</h3>
                  <p className="text-gray-500 text-sm mt-1">{selectedInteraction.callerNumber || 'No number'} &bull; {selectedInteraction.organization || 'No Org'}</p>
                </div>

                <div className="flex flex-wrap gap-2">
                  {getIntentBadge(selectedInteraction.intent)}
                  {getUrgencyBadge(selectedInteraction.urgency_score)}
                  <span className="px-2 py-1 text-xs font-semibold bg-gray-100 text-gray-700 rounded-lg border border-gray-200">
                    Confidence: {100 - selectedInteraction.spam_confidence}%
                  </span>
                </div>

                <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                  <h4 className="text-xs uppercase text-gray-500 font-bold mb-2">Summary</h4>
                  <p className="text-sm text-gray-700 leading-relaxed">{selectedInteraction.summary}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="border border-gray-100 rounded-lg p-3">
                    <h4 className="text-xs uppercase text-gray-500 font-bold mb-1">Sentiment</h4>
                    <p className="text-sm font-medium text-gray-900">{selectedInteraction.sentiment}</p>
                  </div>
                  <div className="border border-gray-100 rounded-lg p-3">
                    <h4 className="text-xs uppercase text-gray-500 font-bold mb-1">Status</h4>
                    <p className="text-sm font-medium text-gray-900">{selectedInteraction.resolution_status}</p>
                  </div>
                </div>



                <div>
                  <h4 className="text-xs uppercase text-gray-500 font-bold mb-3 pl-1">Call Transcript</h4>
                  <div className="bg-[#1e1e1e] text-gray-300 rounded-lg p-4 text-xs font-mono whitespace-pre-wrap leading-relaxed shadow-inner">
                    {selectedInteraction.transcript}
                  </div>
                </div>
              </div>
            )}
           </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
