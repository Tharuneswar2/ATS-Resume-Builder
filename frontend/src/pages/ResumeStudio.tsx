import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { ProfileAPI, ResumeAPI } from '../api/client';
import type { Profile } from '../types';
import { FileText, Download, CheckCircle, AlertTriangle, Loader } from 'lucide-react';

const TEMPLATES = [
  "00_ats_optimized.tex.j2",
  "01_classic_mnc_professional.tex.j2",
  "02_modern_product_company.tex.j2",
  "03_ai_ml_specialist.tex.j2",
  "04_minimalist_executive_mnc.tex.j2",
  "05_bold_modern_startup.tex.j2",
  "06_ats_optimized_style.tex.j2"
];

const ResumeStudio = () => {
  const location = useLocation();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<string>(location.state?.profileId || "");
  const [selectedTemplate, setSelectedTemplate] = useState<string>(TEMPLATES[0]);
  
  const [loadingScore, setLoadingScore] = useState(false);
  const [atsScore, setAtsScore] = useState<any>(null);
  
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchProfiles();
  }, []);

  useEffect(() => {
    if (selectedProfile && selectedTemplate) {
      fetchAtsScore();
    }
  }, [selectedProfile, selectedTemplate]);

  const fetchProfiles = async () => {
    const data = await ProfileAPI.list();
    setProfiles(data);
    if (!selectedProfile && data.length > 0) {
      setSelectedProfile(data[0]._id!);
    }
  };

  const fetchAtsScore = async () => {
    try {
      setLoadingScore(true);
      const score = await ResumeAPI.getAtsScore(selectedProfile, selectedTemplate);
      setAtsScore(score);
    } catch (error) {
      console.error(error);
    } finally {
      setLoadingScore(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      await ResumeAPI.generateAndDownload(selectedProfile, selectedTemplate);
    } catch (error) {
      alert("Failed to generate resume. Check server logs for LaTeX errors.");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="grid grid-cols-2" style={{ gridTemplateColumns: '1fr 1fr', alignItems: 'start' }}>
      
      {/* Configuration Panel */}
      <div className="flex-col gap-3">
        <div className="card glass-panel">
          <h2 className="card-title mb-3">Resume Studio</h2>
          
          <div className="form-group">
            <label className="form-label">Select Profile</label>
            <select 
              className="form-control"
              value={selectedProfile}
              onChange={e => setSelectedProfile(e.target.value)}
            >
              <option value="">-- Choose Profile --</option>
              {profiles.map(p => (
                <option key={p._id} value={p._id}>
                  {p.basic_info?.name} - {p.basic_info?.title}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Select Template</label>
            <div className="flex-col gap-2 mt-2">
              {TEMPLATES.map(t => (
                <label key={t} className="flex items-center gap-2" style={{ cursor: 'pointer' }}>
                  <input 
                    type="radio" 
                    name="template" 
                    value={t} 
                    checked={selectedTemplate === t}
                    onChange={e => setSelectedTemplate(e.target.value)}
                  />
                  <span>{t.replace('.tex.j2', '').replace(/_/g, ' ')}</span>
                </label>
              ))}
            </div>
          </div>

          <button 
            className="btn btn-primary mt-3" 
            onClick={handleGenerate} 
            disabled={generating || !selectedProfile}
            style={{ width: '100%' }}
          >
            {generating ? <Loader className="animate-spin" size={18} /> : <Download size={18} />}
            Generate PDF Resume
          </button>
        </div>
      </div>

      {/* Preview & ATS Panel */}
      <div className="card glass-panel">
        <h3 className="card-title flex justify-between items-center">
          ATS Readiness Score
          {loadingScore && <Loader className="animate-spin" size={18} />}
        </h3>
        
        {!loadingScore && atsScore ? (
          <div>
            <div className="flex items-center gap-3 mt-3 mb-4">
              <div 
                className={`flex items-center justify-center`} 
                style={{
                  width: '80px', height: '80px', borderRadius: '50%', 
                  border: `4px solid ${atsScore.score >= 80 ? 'var(--success-color)' : 'var(--warning-color)'}`,
                  fontSize: '2rem', fontWeight: 'bold'
                }}
              >
                {atsScore.score}
              </div>
              <div>
                <p className="card-title" style={{ color: atsScore.score >= 80 ? 'var(--success-color)' : 'var(--warning-color)' }}>
                  {atsScore.status === 'pass' ? 'Great Match' : 'Needs Improvement'}
                </p>
                <p className="card-subtitle mt-1">{atsScore.recommendation}</p>
              </div>
            </div>

            <h4 className="mb-2">Checks</h4>
            <div className="flex-col gap-2">
              {atsScore.checks.map((check: any, idx: number) => (
                <div key={idx} className="flex items-start gap-2" style={{ padding: '0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: 'var(--radius-sm)' }}>
                  <div className="mt-1">
                    {check.passed 
                      ? <CheckCircle size={16} color="var(--success-color)" /> 
                      : <AlertTriangle size={16} color="var(--warning-color)" />
                    }
                  </div>
                  <div>
                    <p style={{ fontSize: '0.9rem', fontWeight: 500 }}>{check.name}</p>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{check.message}</p>
                  </div>
                  {!check.passed && <div className="ml-auto text-danger text-sm font-bold">-{check.penalty}</div>}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="card-subtitle mt-3">Select a profile and template to view ATS scoring.</p>
        )}
      </div>

    </div>
  );
};

export default ResumeStudio;
