import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Preferences from './pages/Preferences';
import Digests from './pages/Digests';
import DigestDetail from './pages/DigestDetail';

export default function App() {
  return (
    <Router>
      <div className="app-root">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/preferences"
              element={
                <ProtectedRoute>
                  <Preferences />
                </ProtectedRoute>
              }
            />
            <Route
              path="/digests"
              element={
                <ProtectedRoute>
                  <Digests />
                </ProtectedRoute>
              }
            />
            <Route
              path="/digests/:id"
              element={
                <ProtectedRoute>
                  <DigestDetail />
                </ProtectedRoute>
              }
            />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
        <Toaster position="bottom-right" toastOptions={{ style: { background: '#222', color: '#fff' } }} />
      </div>
    </Router>
  );
}
