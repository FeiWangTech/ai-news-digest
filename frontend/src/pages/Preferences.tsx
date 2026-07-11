/* Preferences: protected page with form to update user preferences */
import { useState, useEffect } from 'react';
import { getPreferences, updatePreferences } from '../api/preferences';
import type { PreferencesPayload } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

const AVAILABLE_SOURCES = ['openai', 'huggingface', 'techcrunch', 'arxiv', 'github'];

export default function Preferences() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [emailTime, setEmailTime] = useState('08:00');
  const [timezone, setTimezone] = useState('UTC');
  const [frequency, setFrequency] = useState('daily');
  const [sources, setSources] = useState<string[]>([]);
  const [topics, setTopics] = useState('');
  const [subscribed, setSubscribed] = useState(true);

  useEffect(() => {
    const fetchPreferences = async () => {
      try {
        const { data } = await getPreferences();
        setEmailTime(data.email_time);
        setTimezone(data.timezone);
        setFrequency(data.frequency);
        setSources(data.sources);
        setTopics(data.topics.join(', '));
        setSubscribed(data.subscribed);
      } catch (err) {
        toast.error('Failed to load preferences');
      } finally {
        setLoading(false);
      }
    };
    fetchPreferences();
  }, []);

  const toggleSource = (source: string) => {
    setSources((prev) =>
      prev.includes(source) ? prev.filter((s) => s !== source) : [...prev, source]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: PreferencesPayload = {
        email_time: emailTime,
        timezone,
        frequency,
        sources,
        topics: topics
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean),
        subscribed,
      };
      const { data } = await updatePreferences(payload);
      toast.success(`Preferences saved!`);
      // Sync local state from response
      setEmailTime(data.email_time);
      setTimezone(data.timezone);
      setFrequency(data.frequency);
      setSources(data.sources);
      setTopics(data.topics.join(', '));
      setSubscribed(data.subscribed);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <h1 className="page-title">Preferences</h1>
      <form onSubmit={handleSubmit} className="preferences-form">
        <div className="form-group">
          <label className="form-label">Email Time</label>
          <input
            type="time"
            className="form-input"
            value={emailTime}
            onChange={(e) => setEmailTime(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Timezone</label>
          <select
            className="form-input"
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
          >
            <option value="UTC">UTC</option>
            <option value="US/Eastern">US/Eastern</option>
            <option value="US/Pacific">US/Pacific</option>
            <option value="Europe/London">Europe/London</option>
            <option value="Europe/Berlin">Europe/Berlin</option>
            <option value="Asia/Tokyo">Asia/Tokyo</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Frequency</label>
          <select
            className="form-input"
            value={frequency}
            onChange={(e) => setFrequency(e.target.value)}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="biweekly">Bi-Weekly</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Sources</label>
          <div className="checkbox-group">
            {AVAILABLE_SOURCES.map((source) => (
              <label key={source} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={sources.includes(source)}
                  onChange={() => toggleSource(source)}
                />
                {source}
              </label>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Topics (comma-separated)</label>
          <textarea
            className="form-input textarea"
            value={topics}
            onChange={(e) => setTopics(e.target.value)}
            rows={4}
          />
        </div>

        <div className="form-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={subscribed}
              onChange={(e) => setSubscribed(e.target.checked)}
            />
            Subscribed to digests
          </label>
        </div>

        <button type="submit" className="auth-button" disabled={saving}>
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </form>
    </div>
  );
}
