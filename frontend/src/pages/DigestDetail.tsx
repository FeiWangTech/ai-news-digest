/* DigestDetail: full digest content view with HTML rendering */
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getDigest } from '../api/digests';
import type { Digest } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';

export default function DigestDetail() {
  const { id } = useParams<{ id: string }>();
  const [digest, setDigest] = useState<Digest | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDigest = async () => {
      if (!id) return;
      try {
        const { data } = await getDigest(id);
        setDigest(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchDigest();
  }, [id]);

  if (loading) return <LoadingSpinner />;
  if (!digest) return <div className="page-container"><p>Digest not found.</p></div>;

  const formattedDate = new Date(digest.sent_at).toLocaleString();

  return (
    <div className="page-container">
      <div className="digest-detail-header">
        <div>
          <h1 className="page-title">{digest.subject}</h1>
          <p className="digest-meta">
            Sent: {formattedDate} • Status: <span className={`status-badge status-${digest.status}`}>{digest.status}</span>
          </p>
        </div>
        <Link to="/digests" className="nav-link">Back to Digests</Link>
      </div>

      <div className="digest-content" dangerouslySetInnerHTML={{ __html: digest.html_content }} />

      {digest.items && digest.items.length > 0 && (
        <div className="digest-items">
          <h2 className="section-title">Items</h2>
          <ul className="items-list">
            {digest.items.map((item) => (
              <li key={item.id} className="item-card">
                {item.article_title && <h4>{item.article_title}</h4>}
                {item.summary && <p>{item.summary}</p>}
                {item.article_url && (
                  <a href={item.article_url} target="_blank" rel="noopener noreferrer" className="item-link">
                    Read article
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
