import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ProfileAPI } from '../api/client';
import { Save, Loader, ArrowLeft } from 'lucide-react';

const defaultProfile = {
  basic_info: {
    name: "",
    title: "",
    email: "",
    phone: "",
    location: "",
    links: { linkedin: "", github: "", portfolio: "" }
  },
  professional_summary: { experience_years: 0, core_identity: "", domains: [], key_strengths: [], target_company_alignment: [] },
  skills: { programming: [], ml_ai: [], backend: [], distributed_systems: [], databases: [], data_processing: [], computer_vision: [], cloud_devops: [], developer_tooling: [], tools: [], automation: [], software_engineering: [] },
  experience: [],
  open_source_projects: [],
  projects: [],
  education: [],
  certifications: [],
  awards: [],
  achievement_bank: [],
  preferences: { target_roles: [], work_type: [], industries: [], target_companies: [] },
  writing_style: { tone: "Professional", style: "Impact-driven", rules: [] }
};

const ProfileEditor = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [profileData, setProfileData] = useState<any>(defaultProfile);
  const [jsonInput, setJsonInput] = useState(JSON.stringify(defaultProfile, null, 2));

  useEffect(() => {
    if (id) {
      fetchProfile();
    }
  }, [id]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const data = await ProfileAPI.get(id!);
      // Remove _id for cleaner editing
      const { _id, ...cleanData } = data;
      setProfileData(cleanData);
      setJsonInput(JSON.stringify(cleanData, null, 2));
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleJsonChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setJsonInput(e.target.value);
    try {
      const parsed = JSON.parse(e.target.value);
      setProfileData(parsed);
    } catch (error) {
      // invalid JSON, just let them type
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      let parsedData;
      try {
        parsedData = JSON.parse(jsonInput);
      } catch (err) {
        alert("Invalid JSON format");
        setLoading(false);
        return;
      }

      if (id) {
        await ProfileAPI.update(id, parsedData);
      } else {
        await ProfileAPI.create(parsedData);
      }
      navigate('/');
    } catch (error) {
      console.error(error);
      alert("Error saving profile");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/')} className="btn btn-outline btn-icon">
            <ArrowLeft size={18} />
          </button>
          <h1>{id ? 'Edit Profile' : 'New Profile'}</h1>
        </div>
        <button onClick={handleSave} className="btn btn-primary" disabled={loading}>
          {loading ? <Loader className="animate-spin" size={18} /> : <Save size={18} />}
          Save Profile
        </button>
      </div>

      <div className="card glass-panel">
        <h3 className="card-title mb-2">Profile JSON Editor</h3>
        <p className="card-subtitle mb-3">
          For full control over the schema, edit the profile object below. 
          The data will be validated against the Pydantic schema on the backend.
        </p>
        <textarea 
          className="form-control" 
          style={{ height: '60vh', fontFamily: 'monospace', fontSize: '13px' }}
          value={jsonInput}
          onChange={handleJsonChange}
        />
      </div>
    </div>
  );
};

export default ProfileEditor;
