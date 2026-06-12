import { useEffect, useState } from "react";
import useResumeStore from "../stores/resumeStore";
import useJobStore from "../stores/jobStore";
import DragDropZone from "../components/ui/DragDropZone";
import Select from "../components/ui/Select";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import { CheckCircle, XCircle } from "lucide-react";

export default function Upload() {
  const { uploadResume, uploadLoading, resumes, fetchResumes } =
    useResumeStore();
  const { jobs, fetchJobs } = useJobStore();
  const [selectedJobId, setSelectedJobId] = useState("");
  const [uploadStatus, setUploadStatus] = useState(null);

  useEffect(() => {
    fetchJobs();
    fetchResumes();
  }, [fetchJobs, fetchResumes]);

  const onDrop = async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    try {
      const result = await uploadResume(
        acceptedFiles[0],
        selectedJobId || null,
      );
      setUploadStatus({
        success: true,
        message: `${result.file_name} uploaded successfully`,
      });
      setTimeout(() => setUploadStatus(null), 3000);
    } catch {
      setUploadStatus({ success: false, message: "Upload failed" });
    }
  };

  const jobOptions = jobs.map((j) => ({ value: j.id, label: j.title }));

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Upload Resumes</h1>
      <Card className="mb-8">
        <Select
          label="Associate with job (optional)"
          value={selectedJobId}
          onChange={(e) => setSelectedJobId(e.target.value)}
          options={jobOptions}
          placeholder="No job (standalone)"
        />
        <DragDropZone onDrop={onDrop} />
        {uploadLoading && (
          <p className="text-center text-gray-400 mt-4">Uploading...</p>
        )}
        {uploadStatus && (
          <div
            className={`mt-4 p-3 rounded-md flex items-center ${uploadStatus.success ? "bg-green-900/50 text-green-300" : "bg-red-900/50 text-red-300"}`}
          >
            {uploadStatus.success ? (
              <CheckCircle className="h-5 w-5 mr-2" />
            ) : (
              <XCircle className="h-5 w-5 mr-2" />
            )}
            {uploadStatus.message}
          </div>
        )}
      </Card>
      <h2 className="text-xl font-semibold mb-3">Recent Uploads</h2>
      <div className="space-y-2">
        {resumes.map((r) => (
          <div
            key={r.id}
            className="bg-gray-800 border border-gray-700 rounded-md p-3 flex justify-between items-center"
          >
            <span className="text-gray-200">{r.file_name}</span>
            <span
              className={`text-xs px-2 py-1 rounded ${r.processing_status === "completed" ? "bg-green-900 text-green-300" : "bg-yellow-900 text-yellow-300"}`}
            >
              {r.processing_status || "pending"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
