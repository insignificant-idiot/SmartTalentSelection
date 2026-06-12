import { useEffect, useState } from "react";
import useJobStore from "../stores/jobStore";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Textarea from "../components/ui/Textarea";
import { Briefcase, FileText } from "lucide-react";

export default function Dashboard() {
  const { jobs, fetchJobs, loading, createJob } = useJobStore();
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const handleCreateJob = async (e) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) return;
    setIsCreating(true);
    try {
      await createJob({ title, description });
      setTitle("");
      setDescription("");
      setShowForm(false);
    } catch (error) {
      console.error("Failed to create job", error);
    } finally {
      setIsCreating(false);
    }
  };

  if (loading)
    return <div className="text-center py-10">Loading dashboard...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Job Dashboard</h1>
        <Button onClick={() => setShowForm(!showForm)} variant="secondary">
          {showForm ? (
            <>
              <p className="h-1 w-4 mr-2" /> Cancel
            </>
          ) : (
            <>
              <p className="h-1 w-4 mr-2" /> Add Job
            </>
          )}
        </Button>
      </div>

      {showForm && (
        <Card className="mb-8 border-blue-500 border">
          <form onSubmit={handleCreateJob}>
            <Input
              label="Job Title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Senior Frontend Engineer"
              required
            />
            <Textarea
              label="Job Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Paste the full job description here..."
              rows={5}
              required
            />
            <div className="flex justify-end space-x-3">
              <Button
                type="button"
                variant="secondary"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isCreating}>
                {isCreating ? "Creating..." : "Create Job"}
              </Button>
            </div>
          </form>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {jobs.map((job) => (
          <Card key={job.id} className="hover:border-gray-600 transition">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">
                  {job.title}
                </h3>
                <p className="text-gray-400 text-sm mt-1 line-clamp-2">
                  {job.description}
                </p>
              </div>
              <Briefcase className="h-5 w-5 text-gray-500" />
            </div>
            <div className="mt-4 flex items-center text-sm text-gray-400">
              <FileText className="h-4 w-4 mr-1" />
              <span>{job.resume_count || 0} resumes uploaded</span>
            </div>
          </Card>
        ))}
        {jobs.length === 0 && !showForm && (
          <p className="text-gray-400 col-span-full text-center py-10">
            No jobs found. Click "Add Job" to create one.
          </p>
        )}
      </div>
    </div>
  );
}
