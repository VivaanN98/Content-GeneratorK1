import { useRef, useState } from "react";
import { uploadFile } from "../lib/api";
import type { FileUploadResult } from "../lib/api";

interface Props {
  label: string;
  fieldName: string;
  onUploaded: (result: FileUploadResult) => void;
  onClear: () => void;
}

type UploadState = "idle" | "uploading" | "done" | "error";

export default function FileUpload({ label, fieldName, onUploaded, onClear }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<UploadState>("idle");
  const [fileName, setFileName] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  async function handleFile(file: File) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setErrorMsg("Only PDF files are accepted.");
      setState("error");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setErrorMsg("File must be under 10 MB.");
      setState("error");
      return;
    }

    setState("uploading");
    setFileName(file.name);
    setErrorMsg("");

    try {
      const result = await uploadFile(file, fieldName);
      setState("done");
      onUploaded(result);
    } catch (err: unknown) {
      setState("error");
      setErrorMsg(err instanceof Error ? err.message : "Upload failed");
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }

  function retry() {
    setState("idle");
    setFileName("");
    setErrorMsg("");
    onClear();
    if (inputRef.current) inputRef.current.value = "";
  }

  const borderColor =
    state === "done"
      ? "border-green-400"
      : state === "error"
      ? "border-red-400"
      : "border-gray-300 hover:border-indigo-400";

  return (
    <div
      className={`relative border-2 border-dashed rounded-xl p-4 cursor-pointer transition-colors ${borderColor} bg-white`}
      onClick={() => state === "idle" && inputRef.current?.click()}
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={handleChange}
      />

      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">{label}</p>

      {state === "idle" && (
        <p className="text-sm text-gray-400">Click or drag &amp; drop PDF here</p>
      )}

      {state === "uploading" && (
        <div className="flex items-center gap-2">
          <svg className="animate-spin h-4 w-4 text-indigo-500" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
          </svg>
          <span className="text-sm text-indigo-600">Uploading {fileName}…</span>
        </div>
      )}

      {state === "done" && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg className="h-4 w-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span className="text-sm text-green-700 truncate max-w-[180px]">{fileName}</span>
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); retry(); }}
            className="text-xs text-gray-400 hover:text-red-500 ml-2"
          >
            ✕
          </button>
        </div>
      )}

      {state === "error" && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-red-600">{errorMsg}</span>
          <button
            onClick={(e) => { e.stopPropagation(); retry(); }}
            className="text-xs text-indigo-600 hover:underline ml-2"
          >
            Retry
          </button>
        </div>
      )}
    </div>
  );
}
