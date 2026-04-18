import { useState } from "react";
import FileUpload from "./FileUpload";
import ProgressTracker from "./ProgressTracker";
import { generateContent } from "../lib/api";
import type { FileUploadResult } from "../lib/api";

type StepStatus = "pending" | "running" | "done" | "error";

const CLASS_OPTIONS = ["9", "10", "11", "12"];

const FILE_FIELDS = [
  { fieldName: "syllabus", label: "Syllabus PDF" },
  { fieldName: "chapter", label: "NCERT Chapter PDF" },
  { fieldName: "answers", label: "NCERT Chapter Answers PDF" },
  { fieldName: "all_chapters", label: "All Chapters PDF" },
] as const;

type FieldName = (typeof FILE_FIELDS)[number]["fieldName"];

export default function GenerateForm() {
  const [classNum, setClassNum] = useState("");
  const [subject, setSubject] = useState("");
  const [chapter, setChapter] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<Partial<Record<FieldName, FileUploadResult>>>({});

  const [generating, setGenerating] = useState(false);
  const [stepStatuses, setStepStatuses] = useState<Record<number, StepStatus>>({});
  const [errorMsg, setErrorMsg] = useState("");
  const [docUrl, setDocUrl] = useState<string | null>(null);
  const [docFileName, setDocFileName] = useState("");

  const syllabusUploaded = !!uploadedFiles["syllabus"];
  const canGenerate = classNum && subject && chapter && syllabusUploaded && !generating;

  function handleUploaded(fieldName: FieldName, result: FileUploadResult) {
    setUploadedFiles((prev) => ({ ...prev, [fieldName]: result }));
  }

  function handleClear(fieldName: FieldName) {
    setUploadedFiles((prev) => {
      const next = { ...prev };
      delete next[fieldName];
      return next;
    });
  }

  function downloadDoc() {
    if (!docUrl) return;
    const a = document.createElement("a");
    a.href = docUrl;
    a.download = docFileName;
    a.click();
  }

  async function handleGenerate() {
    setGenerating(true);
    setStepStatuses({});
    setErrorMsg("");
    setDocUrl(null);

    const fileUris = Object.values(uploadedFiles).filter(Boolean) as FileUploadResult[];

    generateContent(
      { class_num: classNum, subject, chapter, file_uris: fileUris },
      (event) => {
        setStepStatuses((prev) => {
          const next = { ...prev };
          if (event.status === "cache") next[0] = "running";
          else if (event.status === "running") {
            next[0] = "done";
            next[event.worker] = "running";
          } else if (event.status === "complete") {
            next[event.worker] = "done";
          } else if (event.status === "document") {
            for (let i = 0; i <= 10; i++) next[i] = "done";
            next[11] = "running";
          }
          return next;
        });
      },
      (docBase64, fileName) => {
        // Mark everything done
        setStepStatuses(() => {
          const next: Record<number, StepStatus> = {};
          for (let i = 0; i <= 11; i++) next[i] = "done";
          return next;
        });

        const bytes = Uint8Array.from(atob(docBase64), (c) => c.charCodeAt(0));
        const blob = new Blob([bytes], {
          type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        });
        setDocUrl(URL.createObjectURL(blob));
        setDocFileName(fileName);
        setGenerating(false);
      },
      (msg) => {
        setErrorMsg(msg);
        setGenerating(false);
        setStepStatuses((prev) => {
          const next = { ...prev };
          // mark running step as error
          for (const [k, v] of Object.entries(next)) {
            if (v === "running") next[Number(k)] = "error";
          }
          return next;
        });
      }
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-10 px-4 space-y-8">
      {/* Metadata */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-4">
        <h2 className="text-lg font-semibold text-gray-800">Content Details</h2>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Class
            </label>
            <select
              value={classNum}
              onChange={(e) => setClassNum(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              <option value="">Select</option>
              {CLASS_OPTIONS.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Subject
            </label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="e.g. Mathematics"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
              Chapter
            </label>
            <input
              type="text"
              value={chapter}
              onChange={(e) => setChapter(e.target.value)}
              placeholder="e.g. Number System"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>
        </div>
      </div>

      {/* File Uploads */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-3">
        <h2 className="text-lg font-semibold text-gray-800">Upload Files</h2>
        <p className="text-xs text-gray-400">Syllabus PDF is required. Others are optional but improve output quality.</p>
        <div className="grid grid-cols-2 gap-3">
          {FILE_FIELDS.map(({ fieldName, label }) => (
            <FileUpload
              key={fieldName}
              label={label}
              fieldName={fieldName}
              onUploaded={(result) => handleUploaded(fieldName, result)}
              onClear={() => handleClear(fieldName)}
            />
          ))}
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={!canGenerate}
        className={`w-full py-3 rounded-xl font-semibold text-sm transition-all ${
          canGenerate
            ? "bg-indigo-600 hover:bg-indigo-700 text-white shadow-md"
            : "bg-gray-200 text-gray-400 cursor-not-allowed"
        }`}
      >
        {generating ? "Generating…" : "Generate Content"}
      </button>

      {/* Progress */}
      {Object.keys(stepStatuses).length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Progress</h2>
          <ProgressTracker stepStatuses={stepStatuses} />
        </div>
      )}

      {/* Error */}
      {errorMsg && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
          {errorMsg}
        </div>
      )}

      {/* Download */}
      {docUrl && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-green-800">Content generated successfully!</p>
            <p className="text-xs text-green-600">{docFileName}</p>
          </div>
          <button
            onClick={downloadDoc}
            className="bg-green-600 hover:bg-green-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
          >
            Download .docx
          </button>
        </div>
      )}
    </div>
  );
}
