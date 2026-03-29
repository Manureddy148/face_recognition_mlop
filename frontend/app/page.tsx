import HeroSection from '@/app/components/HeroSection';
import FeaturesSection from "@/app/components/FeatureSection";
import Link from "next/link";

const buildSnapshot = new Date().toISOString().replace("T", " ").slice(0, 16) + " UTC";

const projectDetails = [
  { label: "Build", value: "Next.js + Flask + DeepFace" },
  { label: "Commit", value: "main / latest auto deploy" },
  { label: "Deploy", value: "GCP Cloud Run" },
  { label: "GitHub", value: "Manureddy148" },
  { label: "Project", value: "project-e553cc0c-7d4a-4519-ade" },
  { label: "Timestamp", value: buildSnapshot },
];

export default function HomePage() {
  return (
    <main className="bg-gradient-to-br from-slate-50 via-white to-blue-50 min-h-screen overflow-hidden">
      {/* Modern Navigation Bar */}
      <nav className="bg-white/90 backdrop-blur-xl border-b border-slate-200/60 shadow-lg sticky top-0 z-50 transition-all duration-300">
        <div className="flex justify-between items-center max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">F</span>
            </div>
            <div className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              FaceRecSys
            </div>
          </div>
          
          <div className="hidden lg:flex space-x-8">
            <a href="#features" className="text-slate-700 hover:text-blue-600 transition-all duration-300 font-medium hover:scale-105 relative group">
              Features
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-600 transition-all duration-300 group-hover:w-full"></span>
            </a>
          </div>
          
          <div className="flex space-x-3">
            <Link
              href="/signin"
              className="px-6 py-2.5 text-blue-600 font-semibold rounded-xl hover:bg-blue-50 transition-all duration-300 border-2 border-blue-200 hover:border-blue-300 hover:scale-105 hover:shadow-lg"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:scale-105 hover:-translate-y-0.5"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Page Content with Smooth Animations */}
      <div className="space-y-24 overflow-hidden pb-12">
        {/* Hero Section */}
        <HeroSection />
        
        {/* Features Section */}
        <section id="features" className="relative">
          <div className="max-w-7xl mx-auto px-4 sm:px-6">
            <FeaturesSection />
          </div>
        </section>

        <section className="relative">
          <div className="max-w-7xl mx-auto px-4 sm:px-6">
            <div className="rounded-3xl border border-slate-200 bg-white/85 backdrop-blur-xl shadow-lg p-6 sm:p-8">
              <div className="max-w-2xl mb-6">
                <p className="text-xs font-semibold tracking-[0.24em] text-blue-600 uppercase">Project Details</p>
                <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-2">Short live project snapshot</h2>
                <p className="text-slate-600 mt-2">Built for attendance capture, running from GitHub to GCP Cloud Run with a unified login and attendance workflow.</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {projectDetails.map((item) => (
                  <div key={item.label} className="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{item.label}</p>
                    <p className="text-sm sm:text-base font-semibold text-slate-900 mt-2 break-words">{item.value}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
        
      </div>
    </main>
  );
}
