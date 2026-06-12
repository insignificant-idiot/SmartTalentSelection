import { useDropzone } from "react-dropzone";
import { Upload } from "lucide-react";

export default function DragDropZone({
  onDrop,
  accept = ".pdf,.docx,.jpg,.jpeg,.png",
}) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
  });
  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive ? "border-blue-500 bg-gray-700" : "border-gray-600 bg-gray-800 hover:bg-gray-700"}`}
    >
      <input {...getInputProps()} />
      <Upload className="mx-auto h-12 w-12 text-gray-400 mb-3" />
      {isDragActive ? (
        <p className="text-gray-300">Drop the files here ...</p>
      ) : (
        <p className="text-gray-300">
          Drag & drop resumes here, or click to select
        </p>
      )}
    </div>
  );
}
