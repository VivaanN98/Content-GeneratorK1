import GenerateForm from "./components/GenerateForm";

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <header className="bg-white border-b border-gray-100 shadow-sm">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <span className="text-white text-sm font-bold">B</span>
          </div>
          <div>
            <h1 className="text-base font-bold text-gray-900 leading-none">Bodhii Content Generator</h1>
            <p className="text-xs text-gray-500 mt-0.5">CBSE Classes 9–12 · Powered by Kimi</p>
          </div>
        </div>
      </header>

      <main>
        <GenerateForm />
      </main>
    </div>
  );
}
