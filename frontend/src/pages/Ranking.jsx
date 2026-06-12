import { useState, useEffect, useRef } from "react";
import useRankingStore from "../stores/rankingStore";
import useJobStore from "../stores/jobStore";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Select from "../components/ui/Select";
import Textarea from "../components/ui/Textarea";
import Spinner from "../components/ui/Spinner";

export default function Ranking() {
  const { jobs, fetchJobs } = useJobStore();
  const { ranking, loading, rankCandidates } = useRankingStore();
  const [selectedJobId, setSelectedJobId] = useState("");
  const [jdText, setJdText] = useState("");
  const [useJobDesc, setUseJobDesc] = useState(true);
  const lastSelectedIdRef = useRef("");
  const prevUseJobDescRef = useRef(useJobDesc);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  // Load job description when selected job changes
  useEffect(() => {
    if (
      useJobDesc &&
      selectedJobId &&
      selectedJobId !== lastSelectedIdRef.current
    ) {
      const job = jobs.find((j) => j.id === parseInt(selectedJobId));
      if (job && job.description) {
        setJdText(job.description);
        lastSelectedIdRef.current = selectedJobId;
      }
    }
  }, [selectedJobId, useJobDesc, jobs]);

  // Handle mode switching without erasing custom text on every render
  useEffect(() => {
    if (useJobDesc !== prevUseJobDescRef.current) {
      if (!useJobDesc) {
        // Switching to custom mode: clear JD text
        setJdText("");
        lastSelectedIdRef.current = "";
      } else {
        // Switching back to job mode: load description if a job is selected
        if (selectedJobId) {
          const job = jobs.find((j) => j.id === parseInt(selectedJobId));
          if (job && job.description) {
            setJdText(job.description);
            lastSelectedIdRef.current = selectedJobId;
          }
        } else {
          setJdText("");
        }
      }
      prevUseJobDescRef.current = useJobDesc;
    }
  }, [useJobDesc, selectedJobId, jobs]);

  const handleRank = async () => {
    if (!jdText.trim()) return;
    await rankCandidates(jdText);
  };

  const jobOptions = jobs.map((j) => ({ value: j.id, label: j.title }));

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Rank Candidates</h1>
      <Card className="mb-8">
        <div className="flex items-center space-x-4 mb-4">
          <label className="flex items-center space-x-2 text-gray-300">
            <input
              type="radio"
              checked={useJobDesc}
              onChange={() => setUseJobDesc(true)}
              className="form-radio bg-gray-700"
            />
            <span>Use job description from existing job</span>
          </label>
          <label className="flex items-center space-x-2 text-gray-300">
            <input
              type="radio"
              checked={!useJobDesc}
              onChange={() => setUseJobDesc(false)}
              className="form-radio bg-gray-700"
            />
            <span>Enter custom JD</span>
          </label>
        </div>
        {useJobDesc && (
          <Select
            label="Select Job"
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
            options={jobOptions}
            placeholder="Choose a job"
          />
        )}
        <Textarea
          label="Job Description"
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
          placeholder="Paste job description here..."
          rows={6}
        />
        <Button onClick={handleRank} disabled={loading || !jdText.trim()}>
          {loading ? <Spinner /> : "Rank Candidates"}
        </Button>
      </Card>
      {ranking && ranking.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Ranked Results</h2>
          <div className="space-y-4">
            {ranking.map((item, idx) => (
              <Card
                key={item.resume_id}
                className="border-l-4 border-l-blue-500"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl font-bold text-blue-400">
                        #{idx + 1}
                      </span>
                      <span className="text-lg font-medium text-white">
                        {item.name || `Resume ID: ${item.resume_id}`}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-4 mt-1 text-sm text-gray-400">
                      <span>📅 {item.years_experience || 0} years exp.</span>
                      <span>🔧 {item.top_skills || "No skills listed"}</span>
                    </div>
                    <p className="text-gray-300 mt-2 text-sm">
                      {item.justification}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-3xl font-bold text-green-400">
                      {item.score}
                    </span>
                    <span className="text-gray-400 text-sm ml-1">/100</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
