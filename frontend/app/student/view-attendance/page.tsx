"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, CalendarDays, Download, Filter, RefreshCcw, Search } from "lucide-react";
// XLSX is dynamically imported in the browser-only export function to avoid
// bundling issues on the server (e.g. "fs" not found). Do not import at module top-level.

interface AttendanceRecord {
  _id: string;
  studentId: string;
  studentName: string;
  date: string;
  subject: string;
  time: string;
  status: "present" | "absent";
  confidence: number | null;
}

export default function ViewAttendance() {
  const router = useRouter();
  const apiBase =
    process.env.NEXT_PUBLIC_API_URL ||
    "https://attendance-backend-aqwtwzewvq-uc.a.run.app";
  const [attendanceData, setAttendanceData] = useState<AttendanceRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState("");
  const [filterDepartment, setFilterDepartment] = useState("");
  const [filterYear, setFilterYear] = useState("");
  const [filterDivision, setFilterDivision] = useState("");
  const [filterSubject, setFilterSubject] = useState("");
  const [filterStudentId, setFilterStudentId] = useState("");
  const [stats, setStats] = useState({
    totalStudents: 0,
    presentToday: 0,
    absentToday: 0,
    attendanceRate: 0,
  });
  const [searched, setSearched] = useState(false);

  const fetchAttendanceData = async () => {
    if (!selectedDate && !filterDepartment) {
      alert("Please select at least one filter.");
      return;
    }
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedDate) params.set("date", selectedDate);
      if (filterDepartment) params.set("department", filterDepartment);
      if (filterYear) params.set("year", filterYear);
      if (filterDivision) params.set("division", filterDivision);
      if (filterSubject) params.set("subject", filterSubject);
      if (filterStudentId) params.set("student_id", filterStudentId);

      const res = await fetch(`${apiBase}/api/attendance?${params.toString()}`);
      const raw = await res.text();
      let data: any;
      try {
        data = JSON.parse(raw);
      } catch (err) {
        console.error("Failed to parse /api/attendance response as JSON. status=", res.status, "body=", raw);
        throw err;
      }

      if (data && data.success) {
        const mappedData: AttendanceRecord[] = data.attendance.map((record: any, idx: number) => ({
          _id: record.studentId || `row-${idx}`,
          studentId: record.studentId || record.student_id || "-",
          studentName: record.studentName || record.student_name || "-",
          date: record.date || data.date || selectedDate,
          subject: record.subject || filterSubject || "-",
          time: record.markedAt || record.time || "-",
          status: record.status || "present",
          confidence: typeof record.confidence === "number" ? record.confidence : null,
        }));
        setAttendanceData(mappedData);
        setStats(data.stats);
      }
      setSearched(true);
    } catch (error) {
      console.error("Error fetching attendance:", error);
    } finally {
      setLoading(false);
    }
  };

  const exportExcel = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedDate) params.set("date", selectedDate);
      if (filterDepartment) params.set("department", filterDepartment);
      if (filterYear) params.set("year", filterYear);
      if (filterDivision) params.set("division", filterDivision);
      if (filterSubject) params.set("subject", filterSubject);

      const res = await fetch(`${apiBase}/api/attendance/export?${params.toString()}`);
      const raw = await res.text();
      let data: any;
      try {
        data = JSON.parse(raw);
      } catch (err) {
        console.error("Failed to parse /api/attendance/export response as JSON. status=", res.status, "body=", raw);
        throw err;
      }
      if (data && data.success) {
        // Dynamic import so bundlers (Next.js SSR) don't try to include node-only deps
        const XLSX = await import("xlsx");
        const worksheet = XLSX.utils.json_to_sheet(data.data);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "Attendance");
        XLSX.writeFile(workbook, `attendance_${selectedDate || "export"}.xlsx`);
      }
    } catch (error) {
      console.error("Error exporting excel:", error);
    }
  };

  const clearFilters = () => {
    setSelectedDate("");
    setFilterDepartment("");
    setFilterYear("");
    setFilterDivision("");
    setFilterSubject("");
    setFilterStudentId("");
    setAttendanceData([]);
    setSearched(false);
    setStats({
      totalStudents: 0,
      presentToday: 0,
      absentToday: 0,
      attendanceRate: 0,
    });
  };

  const formatMarkedAt = (value: string) => {
    if (!value || value === "-") return "-";
    const asDate = new Date(value);
    if (Number.isNaN(asDate.getTime())) return value;
    return `${asDate.toLocaleDateString()} ${asDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50 to-cyan-50 p-4 sm:p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <section className="bg-white/80 backdrop-blur-lg border border-slate-200 rounded-2xl p-5 sm:p-6 shadow-sm">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-800">Attendance Records</h1>
              <p className="text-slate-600 mt-1">Filter by date and subject, review attendance status, and export reports.</p>
            </div>
            <button
              onClick={() => router.push("/dashboard")}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 text-white hover:bg-slate-900 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </button>
          </div>
        </section>

        <section className="bg-white/80 backdrop-blur-lg border border-slate-200 rounded-2xl p-5 sm:p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-4 h-4 text-indigo-600" />
            <h2 className="text-lg font-semibold text-slate-800">Filters</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Date</label>
              <div className="relative">
                <CalendarDays className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg pl-9 pr-3 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Department</label>
              <select
                value={filterDepartment}
                onChange={(e) => setFilterDepartment(e.target.value)}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Departments</option>
                <option value="Computer Science">Computer Science</option>
                <option value="IT">IT</option>
                <option value="Electronics">Electronics</option>
                <option value="Mechanical">Mechanical</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Year</label>
              <select
                value={filterYear}
                onChange={(e) => setFilterYear(e.target.value)}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Years</option>
                <option value="1st Year">1st Year</option>
                <option value="2nd Year">2nd Year</option>
                <option value="3rd Year">3rd Year</option>
                <option value="4th Year">4th Year</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Division</label>
              <select
                value={filterDivision}
                onChange={(e) => setFilterDivision(e.target.value)}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">All Divisions</option>
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Subject</label>
              <input
                value={filterSubject}
                onChange={(e) => setFilterSubject(e.target.value)}
                placeholder="Subject"
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Student ID</label>
              <input
                value={filterStudentId}
                onChange={(e) => setFilterStudentId(e.target.value)}
                placeholder="Student ID"
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-3 mt-4">
            <button
              onClick={fetchAttendanceData}
              disabled={loading}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-60"
            >
              <Search className="w-4 h-4" />
              {loading ? "Searching..." : "Search"}
            </button>
            <button
              onClick={exportExcel}
              disabled={attendanceData.length === 0}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-60"
            >
              <Download className="w-4 h-4" />
              Export Excel
            </button>
            <button
              onClick={clearFilters}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200"
            >
              <RefreshCcw className="w-4 h-4" />
              Clear
            </button>
          </div>
        </section>

        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white border border-slate-200 rounded-xl p-4">
            <p className="text-xs text-slate-500">Total Students</p>
            <p className="text-2xl font-bold text-slate-800 mt-1">{stats.totalStudents}</p>
          </div>
          <div className="bg-white border border-emerald-200 rounded-xl p-4">
            <p className="text-xs text-emerald-600">Present</p>
            <p className="text-2xl font-bold text-emerald-700 mt-1">{stats.presentToday}</p>
          </div>
          <div className="bg-white border border-rose-200 rounded-xl p-4">
            <p className="text-xs text-rose-600">Absent</p>
            <p className="text-2xl font-bold text-rose-700 mt-1">{stats.absentToday}</p>
          </div>
          <div className="bg-white border border-indigo-200 rounded-xl p-4">
            <p className="text-xs text-indigo-600">Attendance Rate</p>
            <p className="text-2xl font-bold text-indigo-700 mt-1">{stats.attendanceRate}%</p>
          </div>
        </section>

        <section className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
          <div className="px-5 py-4 border-b border-slate-200 bg-slate-50">
            <h3 className="text-base font-semibold text-slate-800">
              {selectedDate
                ? `Attendance for ${new Date(selectedDate).toLocaleDateString()}`
                : "Attendance Results"}
            </h3>
          </div>

          {loading ? (
            <div className="p-10 text-center text-slate-600">Loading attendance data...</div>
          ) : !searched ? (
            <div className="p-10 text-center text-slate-500">Apply filters and click Search to load attendance data.</div>
          ) : attendanceData.length === 0 ? (
            <div className="p-10 text-center text-slate-500">No attendance records found for selected filters.</div>
          ) : (
            <div className="overflow-x-auto max-h-[560px]">
              <table className="w-full min-w-[980px]">
                <thead className="bg-slate-100 sticky top-0 z-10">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Student ID</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Name</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Date</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Subject</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Marked At</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {attendanceData.map((record) => (
                    <tr key={record._id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-4 py-3 text-sm font-medium text-slate-800">{record.studentId}</td>
                      <td className="px-4 py-3 text-sm text-slate-700">{record.studentName}</td>
                      <td className="px-4 py-3 text-sm text-slate-700">{new Date(record.date).toLocaleDateString()}</td>
                      <td className="px-4 py-3 text-sm text-slate-700">{record.subject}</td>
                      <td className="px-4 py-3 text-sm text-slate-700">{formatMarkedAt(record.time)}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex px-2.5 py-1 text-xs rounded-full font-medium ${
                            record.status === "present"
                              ? "bg-emerald-100 text-emerald-700"
                              : "bg-rose-100 text-rose-700"
                          }`}
                        >
                          {record.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-700">
                        {record.confidence !== null ? `${record.confidence}%` : "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
