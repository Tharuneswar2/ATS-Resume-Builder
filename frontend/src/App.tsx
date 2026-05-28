import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, UserCircle, FileText, Briefcase } from 'lucide-react';

import Dashboard from './pages/Dashboard';
import ProfileEditor from './pages/ProfileEditor';
import ResumeStudio from './pages/ResumeStudio';
import JDMatcher from './pages/JDMatcher';

function App() {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/profile', label: 'Profiles', icon: <UserCircle size={20} /> },
    { path: '/studio', label: 'Resume Studio', icon: <FileText size={20} /> },
    { path: '/jd-matcher', label: 'JD Matcher', icon: <Briefcase size={20} /> },
  ];

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          AI Resume Gen
        </div>
        <nav className="nav-links">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              {item.icon}
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/profile" element={<ProfileEditor />} />
          <Route path="/profile/:id" element={<ProfileEditor />} />
          <Route path="/studio" element={<ResumeStudio />} />
          <Route path="/jd-matcher" element={<JDMatcher />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
