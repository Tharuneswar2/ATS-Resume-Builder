import React, { useEffect, useState } from 'react';
import { ProfileAPI, JdAPI } from '../api/client';
import type { Profile, JDAnalysis, JDScore } from '../types';
import { Loader, Zap, CheckCircle, XCircle } from 'lucide-react';

const JDMatcher = () => {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<string>("");
  const [jdText, setJdText] = useState("");
  
  const [analyzing, setAnalyzing] = useState(false);
  const [jdAnalysis, setJdAnalysis] = useState<JDAnalysis | null>(null);
  const [jdScore, setJdScore] = useState<JDScore | null>(null);

  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    const data = await ProfileAPI.list();
    setProfiles(data);
    if (data.length > 0) setSelectedProfile(data[0]._id!);
  };

  const handleAnalyze = async () => {
    if (!jdText.trim()) return;
    if (!selectedProfile) {
      alert("Please select a profile first.");
      return;
    }

    try {
      setAnalyzing(true);
      // Run both analysis and scoring in parallel
      const [analysisResult, scoreResult] = await Promise.all([
        JdAPI.analyze(jdText),
        JdAPI.scoreProfile(selectedProfile, jdText)
      ]);
      setJdAnalysis(analysisResult);
      setJdScore(scoreResult);
    } catch (error) {
      console.error(error);
      alert("Analysis failed. Check your API keys and logs.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="grid grid-cols-2" style={{ gridTemplateColumns: '1fr 1fr', alignItems: 'start' }}>
      
      {/* Input Panel */}
      <div className="card glass-panel">
        <h2 className="card-title mb-3">Job Description Matcher</h2>
        
        <div className="form-group">
          <label className="form-label">Select Profile to Match</label>
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
          <label className="form-label">Paste Job Description</label>
          <textarea 
            className="form-control"
            style={{ height: '300px' }}
            placeholder="Paste the full JD text here..."
            value={jdText}
            onChange={e => setJdText(e.target.value)}
          />
        </div>

        <button 
          className="btn btn-primary mt-2" 
          onClick={handleAnalyze} 
          disabled={analyzing || !jdText.trim() || !selectedProfile}
          style={{ width: '100%' }}
        >
          {analyzing ? <Loader className="animate-spin" size={18} /> : <Zap size={18} />}
          Analyze & Score
        </button>
      </div>

      {/* Results Panel */}
      <div className="flex-col gap-3">
        {analyzing ? (
          <div className="card glass-panel flex items-center justify-center" style={{ height: '200px' }}>
            <div className="flex-col items-center gap-3 text-center">
              <Loader className="animate-spin text-primary" size={32} />
              <p className="card-subtitle">AI is analyzing the JD and scoring your profile...</p>
            </div>
          </div>
        ) : jdAnalysis && jdScore ? (
          <>
            <div className="card glass-panel">
              <div className="flex items-center gap-4 mb-4">
                <div 
                  className={`flex items-center justify-center`} 
                  style={{
                    width: '70px', height: '70px', borderRadius: '50%', 
                    border: `4px solid ${jdScore.overall_match >= 70 ? 'var(--success-color)' : 'var(--warning-color)'}`,
                    fontSize: '1.5rem', fontWeight: 'bold'
                  }}
                >
                  {jdScore.overall_match}%
                </div>
                <div>
                  <h3 className="card-title">{jdAnalysis.role}</h3>
                  <p className="card-subtitle">{jdAnalysis.company || 'Unknown Company'}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 mt-2 gap-3">
                <div>
                  <h4 className="mb-2 text-success flex items-center gap-1" style={{ color: 'var(--success-color)' }}>
                    <CheckCircle size={16} /> Matched Keywords
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {jdScore.matched_keywords.map(kw => (
                      <span key={kw} className="tag success">{kw}</span>
                    ))}
                    {jdScore.matched_keywords.length === 0 && <span className="text-secondary text-sm">None</span>}
                  </div>
                </div>
                <div>
                  <h4 className="mb-2 flex items-center gap-1" style={{ color: 'var(--danger-color)' }}>
                    <XCircle size={16} /> Missing Keywords
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {jdScore.missing_keywords.map(kw => (
                      <span key={kw} className="tag" style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger-color)' }}>{kw}</span>
                    ))}
                    {jdScore.missing_keywords.length === 0 && <span className="text-secondary text-sm">None</span>}
                  </div>
                </div>
              </div>
            </div>

            <div className="card glass-panel mt-3">
              <h3 className="card-title mb-3">Extracted Requirements</h3>
              
              <div className="mb-3">
                <p className="form-label font-bold">Required Skills</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {jdAnalysis.required_skills.map(s => <span key={s} className="tag primary">{s}</span>)}
                </div>
              </div>

              <div className="mb-3">
                <p className="form-label font-bold">Preferred Skills</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {jdAnalysis.preferred_skills.map(s => <span key={s} className="tag">{s}</span>)}
                </div>
              </div>

              <div>
                <p className="form-label font-bold">Responsibilities</p>
                <ul style={{ paddingLeft: '1.2rem', marginTop: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  {jdAnalysis.responsibilities.map((r, i) => <li key={i} className="mb-1">{r}</li>)}
                </ul>
              </div>
            </div>
          </>
        ) : (
          <div className="card glass-panel text-center" style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p className="card-subtitle">Paste a JD and click Analyze to see the breakdown and score.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default JDMatcher;
