/* DigestCard: displays digest subject, date, and status */
interface DigestCardProps {
  id: string;
  subject: string;
  sent_at: string;
  status: string;
  onClick?: () => void;
}

export default function DigestCard({ id: _id, subject, sent_at, status, onClick }: DigestCardProps) {
  const formattedDate = new Date(sent_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="digest-card" onClick={onClick} role="button" tabIndex={0}>
      <div className="digest-card-header">
        <h3 className="digest-card-subject">{subject}</h3>
        <span className={`status-badge status-${status}`}>{status}</span>
      </div>
      <p className="digest-card-date">{formattedDate}</p>
      <span className="digest-card-link">View details →</span>
    </div>
  );
}
