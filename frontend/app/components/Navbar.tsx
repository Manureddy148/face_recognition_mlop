"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { logoutUser } from "@/app/lib/auth";

export default function Navbar() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const apiBase =
    process.env.NEXT_PUBLIC_API_URL ||
    "https://attendance-backend-aqwtwzewvq-uc.a.run.app";

  useEffect(() => {
    // Check login status
    const loggedIn = localStorage.getItem("isLoggedIn");
    const storedUsername = localStorage.getItem("username");

    setIsLoggedIn(!!loggedIn);
    setUsername(storedUsername || "");
  }, []);

  const handleLogout = async () => {
    await logoutUser(apiBase);
    setIsLoggedIn(false);
    setUsername("");
    router.push("/signin");
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-gray-800 text-gray-200 px-6 py-4 shadow-lg">
      <div className="flex justify-between items-center max-w-7xl mx-auto">
        {/* Logo */}
        <Link href="/" className="text-2xl font-bold text-blue-400 hover:text-blue-300">
          FaceRecSys
        </Link>

        {/* Navigation Links */}
        <div className="hidden md:flex space-x-6">
          {isLoggedIn ? (
            <>
              {/* Logged in navigation */}
              <Link href="/dashboard" className="hover:text-blue-400 transition-colors">
                Dashboard
              </Link>

              <Link href="/student/registrationform" className="hover:text-blue-400 transition-colors">
                Register Face
              </Link>
              <Link href="/student/updatedetails" className="hover:text-blue-400 transition-colors">
                Update Profile
              </Link>

              <Link href="/student/demo-session" className="hover:text-purple-400 transition-colors">
                Demo
              </Link>
              <Link href="/student/view-attendance" className="hover:text-orange-400 transition-colors">
                Attendance
              </Link>
            </>
          ) : (
            <>
              {/* Guest navigation */}
              <a href="#features" className="hover:text-blue-400 transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="hover:text-blue-400 transition-colors">
                How It Works
              </a>
              <a href="#about" className="hover:text-blue-400 transition-colors">
                About
              </a>
              <a href="#contact" className="hover:text-blue-400 transition-colors">
                Contact
              </a>
            </>
          )}
        </div>

        {/* Auth Buttons */}
        <div className="flex items-center space-x-4">
          {isLoggedIn ? (
            <>
              <span className="text-sm text-gray-300">
                Hello, {username}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 rounded hover:bg-red-700 transition-colors text-sm"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/signin">
                <span className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition-colors text-sm cursor-pointer">
                  Sign In
                </span>
              </Link>
              <Link href="/signup">
                <span className="px-4 py-2 bg-green-600 rounded hover:bg-green-700 transition-colors text-sm cursor-pointer">
                  Sign Up
                </span>
              </Link>
            </>
          )}
        </div>

      </div>
    </nav>
  );
}
