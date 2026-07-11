/* Navbar: responsive top navigation with logo, links, and auth buttons */
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/auth';
import toast from 'react-hot-toast';

export default function Navbar() {
  const { isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">📰</span>
          <span className="logo-text">AI Daily Digest</span>
        </Link>

        <div className="navbar-links">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="nav-link">Dashboard</Link>
              <Link to="/preferences" className="nav-link">Preferences</Link>
              <Link to="/digests" className="nav-link">Digests</Link>
              <button onClick={handleLogout} className="nav-button logout-btn">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="nav-button primary-btn">Sign Up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
