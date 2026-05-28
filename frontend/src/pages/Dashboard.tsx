import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ProfileAPI } from '../api/client';
import type { Profile } from '../types';
import { Plus, Edit2, FileText, Trash2, Loader } from 'lucide-react';

const Dashboard = () => {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchProfiles = async () => {
    try {
      setLoading(true);
      const data = await ProfileAPI.list();
      setProfiles(data);
    } catch (error) {
      console.error("Failed to fetch profiles", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfiles();
  }, []);

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this profile?")) {
      await ProfileAPI.delete(id);
      fetchProfiles();
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h1>Dashboard</h1>
        <Link to="/profile" className="btn btn-primary">
          <Plus size={18} /> New Profile
        </Link>
      </div>

      {loading ? (
        <div className="flex justify-center mt-4">
          <Loader className="animate-spin text-primary" size={32} />
        </div>
      ) : profiles.length === 0 ? (
        <div className="card glass-panel text-center mt-3">
          <h3 className="card-title">No Profiles Found</h3>
          <p className="card-subtitle mt-1">Create your first profile to start generating AI resumes.</p>
          <div className="mt-2">
            <Link to="/profile" className="btn btn-primary">Create Profile</Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-2 mt-3">
          {profiles.map(profile => (
            <div key={profile._id} className="card glass-panel">
              <div>
                <h3 className="card-title">{profile.basic_info?.name || 'Unnamed'}</h3>
                <p className="card-subtitle">{profile.basic_info?.title || 'No Title'}</p>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <span className="tag primary">{profile.experience?.length || 0} Roles</span>
                <span className="tag success">{profile.projects?.length || 0} Projects</span>
              </div>
              <div className="flex gap-2 mt-2">
                <Link to={`/profile/${profile._id}`} className="btn btn-outline" style={{flex: 1}}>
                  <Edit2 size={16} /> Edit
                </Link>
                <button 
                  onClick={() => navigate('/studio', { state: { profileId: profile._id } })}
                  className="btn btn-primary" 
                  style={{flex: 1}}
                >
                  <FileText size={16} /> Studio
                </button>
                <button onClick={() => handleDelete(profile._id!)} className="btn btn-outline btn-icon" style={{color: 'var(--danger-color)', borderColor: 'var(--danger-color)'}}>
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
