/* Digests: protected list of all user digests with pagination */
import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { listDigests } from '../api/digests';
import type { DigestListResponse } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';
import DigestCard from '../components/DigestCard';

const PAGE_SIZE = 10;

export default function Digests() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState<DigestListResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const page = Number(searchParams.get('page') || '1');

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await listDigests(page, PAGE_SIZE);
        setData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [page]);

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;

  if (loading) return <LoadingSpinner />;

  return (
    <div className="page-container">
      <h1 className="page-title">Your Digests</h1>

      {data && data.items.length > 0 ? (
        <>
          <div className="digest-list">
            {data.items.map((d) => (
              <Link key={d.id} to={`/digests/${d.id}`}>
                <DigestCard {...d} />
              </Link>
            ))}
          </div>

          <div className="pagination">
            <button
              className="pagination-btn"
              disabled={page <= 1}
              onClick={() => setSearchParams({ page: String(page - 1) })}
            >
              Previous
            </button>
            <span className="pagination-info">
              Page {page} of {totalPages} ({data.total} total)
            </span>
            <button
              className="pagination-btn"
              disabled={page >= totalPages}
              onClick={() => setSearchParams({ page: String(page + 1) })}
            >
              Next
            </button>
          </div>
        </>
      ) : (
        <p className="empty-state">No digests yet.</p>
      )}
    </div>
  );
}
