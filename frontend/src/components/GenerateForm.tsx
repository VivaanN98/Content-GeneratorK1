import { useState } from "react";
import FileUpload from "./FileUpload";
import ProgressTracker from "./ProgressTracker";
import { generateContent, parseSyllabus } from "../lib/api";
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

const OPTIONAL_FIELDS: FieldName[] = ["chapter", "answers", "all_chapters"];

export default function GenerateForm() {
  const [classNum, setClassNum] = useState("");
  const [subject, setSubject] = useState("");
  const [chapter, setChapter] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<Partial<Record<FieldName, FileUploadResult>>>({});

  // Chapter-picker state
  const [chapters, setChapters] = useState<string[]>([]);
  const [loadingChapters, setLoadingChapters] = useState(false);
  const [chaptersError, setChaptersError] = useState<string | null>(null);
  const [manualMode, setManualMode] = useState(false);

  const [generating, setGenerating] = useState(false);
  const [stepStatuses, setStepStatuses] = useState<Record<number, StepStatus>>({});
  const [errorMsg, setErrorMsg] = useState("");
  const [docUrl, setDocUrl] = useState<string | null>(null);
  const [docFileName, setDocFileName] = useState("");

  const syllabusUploaded = !!uploadedFiles["syllabus"];
  const chaptersLoaded = chapters.length > 0;
  const optionalUploadsDisabled = chaptersLoaded;

  // Load Chapters button enabled when all three prerequisites are met and we're not already in picker/manual mode
  const canLoadChapters =
    !!classNum && !!subject && syllabusUploaded && !chaptersLoaded && !loadingChapters && !manualMode;

  const canGenerate = classNum && subject && chapter && syllabusUploaded && !generating;

  function resetChapterState() {
    setChapters([]);
    setChaptersError(null);
    setManualMode(false);
    setChapter("");
  }

  function handleClassChange(val: string) {
    setClassNum(val);
    resetChapterState();
  }

  function handleSubjectChange(val: string) {
    setSubject(val);
    resetChapterState();
  }

  function handleUploaded(fieldName: FieldName, result: FileUploadResult) {
    setUploadedFiles((prev) => ({ ...prev, [fieldName]: result }));
    if (fieldName === "syllabus") resetChapterState();
  }

  function handleClear(fieldName: FieldName) {
    setUploadedFiles((prev) => {
      const next = { ...prev };
      delete next[fieldName];
      return next;
    });
    if (fieldName === "syllabus") resetChapterState();
  }

  async function handleLoadChapters() {
    const syllabusResult = uploadedFiles["syllabus"];
    if (!syllabusResult) return;
    setLoadingChapters(true);
    setChaptersError(null);
    try {
      const list = await parseSyllabus(syllabusResult.uri, classNum, subject);
      setChapters(list);
    } catch (err: unknown) {
      setChaptersError(err instanceof Error ? err.message : "Failed to parse syllabus.");
    } finally {
      setLoadingChapters(false);
    }
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

    // When chapters are loaded (Path B), only pass the syllabus PDF
    const fileUris = chaptersLoaded
      ? [uploadedFiles["syllabus"]!]
      : (Object.values(uploadedFiles).filter(Boolean) as FileUploadResult[]);

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
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 space-y-4">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Content Details</h2>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              Class
            </label>
            <select
              value={classNum}
              onChange={(e) => handleClassChange(e.target.value)}
              className="w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
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
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              Subject
            </label>
            <input
              type="text"
              value={subject}
              onChange={(e) => handleSubjectChange(e.target.value)}
              placeholder="e.g. Mathematics"
              className="w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              Chapter
            </label>
            {chaptersLoaded ? (
              <select
                value={chapter}
                onChange={(e) => setChapter(e.target.value)}
                className="w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              >
                <option value="">Select chapter…</option>
                {chapters.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value={chapter}
                onChange={(e) => setChapter(e.target.value)}
                placeholder="e.g. Number System"
                className="w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-500 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
            )}
          </div>
        </div>
      </div>

      {/* File Uploads */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6 space-y-3">
        <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100">Upload Files</h2>
        <p className="text-xs text-gray-400 dark:text-gray-500">Syllabus PDF is required. Others are optional but improve output quality.</p>
        <div className="grid grid-cols-2 gap-3">
          {FILE_FIELDS.map(({ fieldName, label }) => (
            <FileUpload
              key={fieldName}
              label={label}
              fieldName={fieldName}
              disabled={OPTIONAL_FIELDS.includes(fieldName as FieldName) && optionalUploadsDisabled}
              onUploaded={(result) => handleUploaded(fieldName, result)}
              onClear={() => handleClear(fieldName)}
            />
          ))}
        </div>

        {/* Load Chapters row */}
        <div className="pt-1 space-y-2">
          <div className="flex items-center gap-3">
            <button
              onClick={handleLoadChapters}
              disabled={!canLoadChapters}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                canLoadChapters
                  ? "bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 border border-indigo-300 dark:border-indigo-700 hover:bg-indigo-100 dark:hover:bg-indigo-900/50"
                  : "bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-600 border border-gray-200 dark:border-gray-700 cursor-not-allowed"
              }`}
            >
              {loadingChapters ? (
                <>
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  Loading chapters…
                </>
              ) : (
                "Load Chapters from Syllabus"
              )}
            </button>

            {(chaptersLoaded || manualMode || chaptersError) && (
              <button
                onClick={resetChapterState}
                className="text-xs text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400 transition-colors"
              >
                Reset
              </button>
            )}
          </div>

          {chaptersError && (
            <div className="text-sm text-red-600 dark:text-red-400 space-y-1">
              <p>{chaptersError}</p>
              <button
                onClick={() => { setManualMode(true); setChaptersError(null); }}
                className="text-indigo-600 dark:text-indigo-400 hover:underline text-xs"
              >
                Enter chapter manually instead
              </button>
            </div>
          )}

          {chaptersLoaded && (
            <p className="text-xs text-indigo-600 dark:text-indigo-400">
              {chapters.length} chapters loaded — select one above. Other PDF uploads are disabled for this path.
            </p>
          )}
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={!canGenerate}
        className={`w-full py-3 rounded-xl font-semibold text-sm transition-all ${
          canGenerate
            ? "bg-indigo-600 hover:bg-indigo-700 text-white shadow-md"
            : "bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed"
        }`}
      >
        {generating ? "Generating…" : "Generate Content"}
      </button>

      {/* Progress */}
      {Object.keys(stepStatuses).length > 0 && (
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-4">Progress</h2>
          <ProgressTracker stepStatuses={stepStatuses} />
        </div>
      )}

      {/* Error */}
      {errorMsg && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 text-sm text-red-700 dark:text-red-400">
          {errorMsg}
        </div>
      )}

      {/* Download */}
      {docUrl && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-green-800 dark:text-green-300">Content generated successfully!</p>
            <p className="text-xs text-green-600 dark:text-green-400">{docFileName}</p>
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
