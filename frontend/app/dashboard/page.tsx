"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { 
  Users, 
  Edit3, 
  Camera, 
  BarChart3, 
  LogOut, 
  User,
  Play
} from "lucide-react";
import { logoutUser } from "@/app/lib/auth";

export default function DashboardPage() {
  const router = useRouter();
  const apiBase =
    process.env.NEXT_PUBLIC_API_URL ||
    "https://attendance-backend-aqwtwzewvq-uc.a.run.app";
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);
  const [username, setUsername] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [activeCard, setActiveCard] = useState<number | null>(null);

  useEffect(() => {
    const checkAuthStatus = () => {
      try {
        const loggedIn = localStorage.getItem("isLoggedIn");
        const storedUsername = localStorage.getItem("username");
        const storedEmail = localStorage.getItem("userEmail");
        
        if (!loggedIn || loggedIn !== "true") {
          setIsLoggedIn(false);
          router.push("/signin");
        } else {
          setIsLoggedIn(true);
          setUsername(storedUsername || "User");
          setUserEmail(storedEmail || "");
        }
      } catch (error) {
        console.error("localStorage not available:", error);
        setIsLoggedIn(false);
        router.push("/signin");
      }
    };

    const timeoutId = setTimeout(checkAuthStatus, 100);
    return () => clearTimeout(timeoutId);
  }, [router]);

  const handleLogout = async () => {
    await logoutUser(apiBase);
    router.push("/signin");
  };

  const studentManagementOptions = [
    {
      title: "Student Registration",
      description: "Register new students with complete details and face recognition setup",
      icon: <Users className="w-7 h-7" />,
      path: "/student/registrationform",
      color: "from-blue-500 to-blue-600",
      bgColor: "bg-blue-50 hover:bg-blue-100",
      borderColor: "border-blue-200 hover:border-blue-300",
      iconBg: "bg-blue-500"
    },
    {
      title: "Update Student Details",
      description: "Modify existing student information and profile settings",
      icon: <Edit3 className="w-7 h-7" />,
      path: "/student/updatedetails",
      color: "from-emerald-500 to-emerald-600",
      bgColor: "bg-emerald-50 hover:bg-emerald-100",
      borderColor: "border-emerald-200 hover:border-emerald-300",
      iconBg: "bg-emerald-500"
    },
    {
      title: "Face Recognition",
      description: "Test and demonstrate live face recognition capabilities",
      icon: <Camera className="w-7 h-7" />,
      path: "/student/demo-session",
      color: "from-purple-500 to-purple-600",
      bgColor: "bg-purple-50 hover:bg-purple-100",
      borderColor: "border-purple-200 hover:border-purple-300",
      iconBg: "bg-purple-500"
    },
    {
      title: "Start Face Recognition",
      description: "Start attendance capture for a selected class and subject",
      icon: <Play className="w-7 h-7" />,
      path: "/teacher/start-session",
      color: "from-fuchsia-500 to-violet-600",
      bgColor: "bg-fuchsia-50 hover:bg-fuchsia-100",
      borderColor: "border-fuchsia-200 hover:border-fuchsia-300",
      iconBg: "bg-fuchsia-500"
    },
    {
      title: "Attendance Records",
      description: "View comprehensive attendance statistics and reports",
      icon: <BarChart3 className="w-7 h-7" />,
      path: "/student/view-attendance",
      color: "from-amber-500 to-orange-500",
      bgColor: "bg-amber-50 hover:bg-amber-100",
      borderColor: "border-amber-200 hover:border-amber-300",
      iconBg: "bg-amber-500"
    }
  ];

  if (isLoggedIn === null) {
    return (
      <div className="flex items-center justify-center w-full h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto mb-4"></div>
          <p className="text-xl text-slate-700 font-medium">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (isLoggedIn === false) {
    return (
      <div className="flex items-center justify-center w-full h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-red-500 mx-auto mb-4"></div>
          <p className="text-xl text-slate-700 font-medium">Redirecting to sign in...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200 shadow-sm">
        <div className="px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Left Section */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-lg">
                  <User className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl sm:text-2xl font-bold text-slate-800 tracking-tight">Dashboard</h1>
                  <p className="text-slate-600 text-sm font-medium">Welcome back, {username}</p>
                  {userEmail && <p className="text-slate-500 text-xs">{userEmail}</p>}
                </div>
              </div>
            </div>

            {/* Right Section */}
            <div className="flex items-center gap-2 sm:gap-4">
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 sm:px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-colors border border-red-200 hover:border-red-300"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:block font-medium">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-4 sm:px-6 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Welcome Message */}
          <div className="mb-12 text-center">
            <div className="inline-flex items-center gap-3 mb-4">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span className="text-blue-600 font-semibold text-sm uppercase tracking-wider">Dashboard</span>
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-800 mb-3 tracking-tight">
              Student Management Hub
            </h2>
            <p className="text-slate-600 text-lg max-w-2xl mx-auto leading-relaxed">
              Use one place for registration, recognition, attendance sessions, and attendance records.
            </p>
          </div>

          {/* Tools Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
            {studentManagementOptions.map((option, index) => (
              <div
                key={index}
                onMouseEnter={() => setActiveCard(index)}
                onMouseLeave={() => setActiveCard(null)}
                onClick={() => router.push(option.path)}
                className={`relative p-6 rounded-2xl border-2 transition-all duration-500 cursor-pointer group overflow-hidden bg-white hover:shadow-xl ${
                  option.borderColor
                } ${
                  activeCard === index ? 'scale-105 shadow-xl -translate-y-1' : 'hover:scale-105 hover:-translate-y-1'
                }`}
              >
                {/* Animated Background */}
                <div className={`absolute inset-0 bg-gradient-to-br ${option.color} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />
                
                {/* Content */}
                <div className="relative z-10">
                  <div className={`p-4 rounded-xl bg-gradient-to-br ${option.color} w-fit mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                    <div className="text-white">
                      {option.icon}
                    </div>
                  </div>
                  
                  <h4 className="text-xl font-bold text-slate-800 mb-3 group-hover:text-slate-900 transition-colors">
                    {option.title}
                  </h4>
                  
                  <p className="text-slate-600 text-sm mb-6 leading-relaxed line-clamp-3">
                    {option.description}
                  </p>
                  
                  <div className={`inline-flex items-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r ${option.color} text-white font-semibold text-sm transition-all duration-300 group-hover:gap-3 group-hover:shadow-lg group-hover:scale-105`}>
                    Get Started
                    <svg className="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>

                {/* Decorative Elements */}
                <div className="absolute top-4 right-4 w-20 h-20 bg-gradient-to-br from-slate-100 to-slate-200 rounded-full opacity-20 group-hover:opacity-30 transition-opacity"></div>
                <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-gradient-to-br from-slate-100 to-slate-200 rounded-full opacity-10 group-hover:opacity-20 transition-opacity"></div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}