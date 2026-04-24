const API_URL = import.meta.env.VITE_API_URL as string;

export interface FileUploadResult {
  uri: string;
  mime_type: string;
  field_name: string;
  file_name: string;
}

export interface ProgressEvent {
  worker: number;
  status: "cache" | "running" | "complete" | "document";
  message: string;
}

export interface GenerateParams {
  class_num: string;
  subject: string;
  chapter: string;
  file_uris: FileUploadResult[];
}

export async function parseSyllabus(
  syllabusUri: string,
  classNum: string,
  subject: string
): Promise<string[]> {
  const res = await fetch(`${API_URL}/api/parse-syllabus`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ syllabus_uri: syllabusUri, class_num: classNum, subject }),
  });

  if (!res.ok) {
    let detail = `Parse failed (${res.status})`;
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }

  const data = await res.json();
  return data.chapters as string[];
}

export async function uploadFile(
  file: File,
  fieldName: string
): Promise<FileUploadResult> {
  const form = new FormData();
  form.append("file", file);
  form.append("field_name", fieldName);

  const res = await fetch(`${API_URL}/api/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Upload failed: ${text}`);
  }

  return res.json();
}

export function generateContent(
  params: GenerateParams,
  onProgress: (e: ProgressEvent) => void,
  onComplete: (docBase64: string, fileName: string) => void,
  onError: (msg: string) => void
): () => void {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${API_URL}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params),
        signal: controller.signal,
      });

      if (!res.ok || !res.body) {
        onError(`Generate request failed: ${res.status}`);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let eventType = "";
      let dataLine = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            eventType = line.slice(7).trim();
          } else if (line.startsWith("data: ")) {
            dataLine = line.slice(6).trim();
          } else if (line === "" && eventType && dataLine) {
            try {
              const parsed = JSON.parse(dataLine);
              if (eventType === "progress") {
                onProgress(parsed as ProgressEvent);
              } else if (eventType === "complete") {
                onComplete(parsed.document, parsed.file_name);
              } else if (eventType === "error") {
                onError(parsed.message ?? "Unknown error");
              }
            } catch {
              // ignore parse errors on individual events
            }
            eventType = "";
            dataLine = "";
          }
        }
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name !== "AbortError") {
        onError(err.message);
      }
    }
  })();

  return () => controller.abort();
}
