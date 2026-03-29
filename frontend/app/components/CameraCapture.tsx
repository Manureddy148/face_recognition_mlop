"use client";

import React, { useRef, useEffect, useState } from "react";

export interface FaceData {
  box: [number, number, number, number];
  match: { user_id: string; name: string } | null;
  confidence?: number;
}

interface CameraCaptureProps {
  onCapture: (dataUrl: string) => void | Promise<void>;
  captureIntervalMs?: number | null;
  singleShot?: boolean;
  isLiveMode?: boolean;
  facesData?: FaceData[];
}

const CameraCapture: React.FC<CameraCaptureProps> = ({
  onCapture,
  captureIntervalMs = null,
  singleShot = false,
  isLiveMode = false,
  facesData = [],
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const onCaptureRef = useRef(onCapture);
  const facesDataRef = useRef(facesData);
  const isCapturingRef = useRef(false);
  const [cameraStatus, setCameraStatus] = useState<"loading" | "active" | "stopped">("stopped");
  const [cameraError, setCameraError] = useState<string>("");

  useEffect(() => {
    onCaptureRef.current = onCapture;
  }, [onCapture]);

  useEffect(() => {
    facesDataRef.current = facesData;
  }, [facesData]);

  const startCamera = async () => {
    try {
      setCameraStatus("loading");
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
      });
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraStatus("active");
    } catch (err) {
      console.error("Camera error:", err);
      setCameraError("Failed to access camera.");
      setCameraStatus("stopped");
    }
  };

  const stopCamera = () => {
    const stream = videoRef.current?.srcObject as MediaStream;
    stream?.getTracks().forEach((track) => track.stop());
    if (videoRef.current) videoRef.current.srcObject = null;
    if (intervalRef.current) clearInterval(intervalRef.current);
    setCameraStatus("stopped");
  };

  const drawOverlay = () => {
    const video = videoRef.current;
    const overlayCanvas = overlayCanvasRef.current;
    if (!video || !overlayCanvas || cameraStatus !== "active") return;

    overlayCanvas.width = video.videoWidth || 640;
    overlayCanvas.height = video.videoHeight || 480;
    const overlayCtx = overlayCanvas.getContext("2d");
    if (!overlayCtx) return;

    overlayCtx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);

    facesDataRef.current.forEach((face) => {
      const [x, y, w, h] = face.box;
      overlayCtx.strokeStyle = face.match ? "lime" : "red";
      overlayCtx.lineWidth = 2;
      overlayCtx.strokeRect(x, y, w, h);

      overlayCtx.fillStyle = face.match ? "lime" : "red";
      overlayCtx.font = "16px Arial";
      overlayCtx.fillText(
        face.match ? `${face.match.name} (${face.match.user_id})` : "Unknown",
        x,
        Math.max(16, y - 5)
      );
    });
  };

  const capture = async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || cameraStatus !== "active" || isCapturingRef.current) return;

    isCapturingRef.current = true;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      isCapturingRef.current = false;
      return;
    }

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataUrl = canvas.toDataURL("image/jpeg", 0.8);
    try {
      await onCaptureRef.current(dataUrl);
    } finally {
      isCapturingRef.current = false;
    }
  };

  useEffect(() => {
    if (singleShot || isLiveMode) startCamera();
    return () => stopCamera();
  }, [singleShot, isLiveMode]);

  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (captureIntervalMs && isLiveMode && cameraStatus === "active") {
      intervalRef.current = setInterval(() => {
        void capture();
      }, captureIntervalMs);
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [captureIntervalMs, isLiveMode, cameraStatus]);

  useEffect(() => {
    drawOverlay();
  }, [facesData, cameraStatus]);

  return (
    <div className="relative w-full max-w-md">
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className={`rounded-lg shadow-md w-full ${cameraStatus === "active" ? "block" : "hidden"}`}
        style={{ maxHeight: "360px" }}
      />
      <canvas ref={overlayCanvasRef} className="absolute top-0 left-0 rounded-lg w-full h-full pointer-events-none" />
      <canvas ref={canvasRef} className="hidden" />
      {cameraStatus === "stopped" && !cameraError && (
        <button
          onClick={startCamera}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-blue-600 text-white px-4 py-2 rounded"
        >
          Start Camera
        </button>
      )}
      {cameraError && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-red-600">
          {cameraError}
        </div>
      )}
    </div>
  );
};

export default CameraCapture;
