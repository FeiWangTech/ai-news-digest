/* Dashboard: protected page showing recent digests and quick stats */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { listDigests, generateDigest } from '../api/digests';
import { getPreferences } from '../api/preferences';
import type { DigestListResponse, Preference } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import DigestCard from '../components/DigestCard';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const [digests, setDigests] = useState<DigestListResponse | null>(null);
  const [prefs, setPrefs] = useState<Preference | null>(null);
  const [loading, setLoading] = useState(true);
  const [genLoading, setGenLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [digestsRes, prefsRes] = await Promise.all([listDigests(), getPreferences()]);
        setDigests(digestsRes.data);
        setPrefs(prefsRes.data);
      } catch (err) {
        toast.error('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleGenerate = async () => {
    setGenLoading(true);
    try {
      await generateDigest();
      toast.success('Digest generation triggered');
      const res = await listDigests();
      setDigests(res.data);
    } catch {
      toast.error('Failed to trigger digest generation');
    } finally {
      setGenLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <button className="primary-btn" onClick={handleGenerate} disabled={genLoading}>
          {genLoading ? 'Generating...' : 'Generate Digest Now'}
        </button>
      </div>

      {prefs && (
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-label">Frequency</span>
            <span className="stat-value">{prefs.frequency}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Timezone</span>
            <span className="stat-value">{prefs.timezone}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Subscribed</span>
            <span className="stat-value">{prefs.subscribed ? 'Yes' : 'No'}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Sources</span>
            <span className="stat-value">{prefs.sources.length}</span>
          </div>
        </div>
      )}

      <div className="section">
        <h2 className="section-title">Recent Digests</h2>
        {digests && digests.items.length > 0 ? (
          <div className="digest-list">
            {digests.items.slice(0, 5).map((d) => (
              <Link key={d.id} to={`/digests/${d.id}`}>
                <DigestCard {...d} />
              </Link>
            ))}
          </div>
        ) : (
          <p className="empty-state">No digests yet. Generate your first one!</p>
        )}
      </div>
    </div>
  );
}
