interface Step {
  id: number;
  label: string;
}

const STEPS: Step[] = [
  { id: 0,  label: "Preparing Context" },
  { id: 1,  label: "Core Learning" },
  { id: 2,  label: "Memory" },
  { id: 3,  label: "MCQs" },
  { id: 4,  label: "Very Short Questions" },
  { id: 5,  label: "Short Answer Questions" },
  { id: 6,  label: "Medium Answer Questions" },
  { id: 7,  label: "Long Answer Questions" },
  { id: 8,  label: "Assertion-Reason" },
  { id: 9,  label: "Case Studies" },
  { id: 10, label: "Test Generation" },
  { id: 11, label: "Generating Document" },
];

type StepStatus = "pending" | "running" | "done" | "error";

interface Props {
  stepStatuses: Record<number, StepStatus>;
}

function StepIcon({ status }: { status: StepStatus }) {
  if (status === "done") {
    return (
      <div className="flex items-center justify-center w-7 h-7 rounded-full bg-green-100 border-2 border-green-500">
        <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>
    );
  }
  if (status === "running") {
    return (
      <div className="flex items-center justify-center w-7 h-7 rounded-full bg-indigo-100 border-2 border-indigo-500">
        <svg className="animate-spin w-4 h-4 text-indigo-600" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
      </div>
    );
  }
  if (status === "error") {
    return (
      <div className="flex items-center justify-center w-7 h-7 rounded-full bg-red-100 border-2 border-red-500">
        <span className="text-red-600 text-xs font-bold">✕</span>
      </div>
    );
  }
  return (
    <div className="flex items-center justify-center w-7 h-7 rounded-full bg-gray-100 border-2 border-gray-300">
      <div className="w-2 h-2 rounded-full bg-gray-300" />
    </div>
  );
}

export default function ProgressTracker({ stepStatuses }: Props) {
  return (
    <div className="space-y-2">
      {STEPS.map((step, idx) => {
        const status = stepStatuses[step.id] ?? "pending";
        return (
          <div key={step.id} className="flex items-center gap-3">
            <div className="flex flex-col items-center">
              <StepIcon status={status} />
              {idx < STEPS.length - 1 && (
                <div className={`w-0.5 h-5 mt-1 ${status === "done" ? "bg-green-300" : "bg-gray-200"}`} />
              )}
            </div>
            <span
              className={`text-sm ${
                status === "running"
                  ? "text-indigo-700 font-semibold"
                  : status === "done"
                  ? "text-green-700"
                  : status === "error"
                  ? "text-red-600"
                  : "text-gray-400"
              }`}
            >
              {step.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
