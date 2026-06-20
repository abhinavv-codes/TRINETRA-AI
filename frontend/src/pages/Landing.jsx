import React, { useState, useRef } from 'react';
import toast from 'react-hot-toast';

// Simple SVG Icons
const UploadIcon = () => (
  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
  </svg>
);

const PlayIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
    <path d="M8 5v14l11-7z" />
  </svg>
);

const AlertIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4v2m0 0v2m0-2H9m3 0h3m-3-7a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

export default function Landing() {
  const [video, setVideo] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const [enhancedFrames, setEnhancedFrames] = useState([]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const validateVideo = (file) => {
    const validTypes = ['video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo'];
    const maxSize = 500 * 1024 * 1024; // 500MB

    if (!validTypes.includes(file.type)) {
      toast.error('Please upload a valid video file (MP4, MOV, AVI)');
      return false;
    }

    if (file.size > maxSize) {
      toast.error('Video size must be less than 500MB');
      return false;
    }

    return true;
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const file = files[0];
      if (validateVideo(file)) {
        setVideo(file);
        const preview = URL.createObjectURL(file);
        setVideoPreview(preview);
      }
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file && validateVideo(file)) {
      setVideo(file);
      const preview = URL.createObjectURL(file);
      setVideoPreview(preview);
    }
  };

  const handleUpload = async () => {
    if (!video) {
      toast.error('Please select a video first');
      return;
    }

    setIsLoading(true);
    try {
      // TODO: Replace with your actual API endpoint
      // For now, just show success after a short delay
      const formData = new FormData();

        formData.append(
        "video",
        video
        );

        const response = await fetch(
        "http://localhost:8000/test-enhancement",
        {
            method: "POST",
            body: formData,
        }
        );

        const data = await response.json();

        setEnhancedFrames(
        data.frames
        );

        toast.success(
        "Processed successfully"
        );
      
      toast.success('Video uploaded successfully!');
      setVideo(null);
      setVideoPreview(null);
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Error uploading video');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setVideo(null);
    setVideoPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-slate-900/80 border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">T</span>
              </div>
              <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-red-600">
                TRINETRA-AI
              </h1>
            </div>
            <p className="text-slate-400 text-sm font-medium">Traffic Violation Detection</p>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="min-h-[calc(100vh-64px)] flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-2xl">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h2 className="text-4xl sm:text-5xl font-bold text-white mb-4">
              Intelligent Video Analysis
            </h2>
            <p className="text-lg text-slate-300 mb-2">
              Upload your traffic surveillance video for AI-powered violation detection
            </p>
            <p className="text-sm text-slate-400">
              Advanced computer vision with real-time processing
            </p>
          </div>

          {/* Upload Section */}
          <div className="space-y-6">
            {/* Video Preview or Upload Area */}
            {videoPreview ? (
              <div className="relative group">
                <video
                  src={videoPreview}
                  controls
                  className="w-full h-80 rounded-2xl object-cover shadow-2xl border border-slate-700"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/50 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </div>
            ) : (
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
                  isDragActive
                    ? 'border-red-500 bg-red-500/10 scale-105'
                    : 'border-slate-600 hover:border-slate-500 bg-slate-800/50 hover:bg-slate-800/70'
                }`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  accept="video/*"
                  className="hidden"
                />

                <div className="flex flex-col items-center gap-4">
                  <div className={`p-4 rounded-full transition-colors ${
                    isDragActive ? 'bg-red-500/20' : 'bg-slate-700/50'
                  }`}>
                    <div className={`${isDragActive ? 'text-red-400' : 'text-slate-300'}`}>
                      <UploadIcon />
                    </div>
                  </div>

                  <div>
                    <p className="text-xl font-semibold text-white mb-1">
                      {isDragActive ? 'Drop your video here' : 'Drag & drop your video'}
                    </p>
                    <p className="text-slate-400 text-sm">
                      or click to browse • MP4, MOV, AVI • Up to 500MB
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Info Box */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 flex gap-3">
              <div className="text-slate-400 flex-shrink-0 mt-0.5">
                <AlertIcon />
              </div>
              <p className="text-sm text-slate-300">
                Your video will be processed with our advanced AI model to detect traffic violations in real-time.
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-center">
              {video && (
                <>
                  <button
                    onClick={handleClear}
                    disabled={isLoading}
                    className="px-6 py-3 rounded-xl font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Clear
                  </button>
                  <button
                    onClick={handleUpload}
                    disabled={isLoading}
                    className="px-8 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 shadow-lg hover:shadow-red-500/25 transition-all duration-200 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <PlayIcon />
                        Analyze Video
                      </>
                    )}
                  </button>
                </>
              )}
            </div>
            
            {enhancedFrames.length > 0 && (
            <div className="mt-8">
                <h3 className="text-2xl font-bold text-white mb-4">
                First 10 Enhanced Frames
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {enhancedFrames.map(
                    (frame, index) => (
                    <img
                        key={index}
                        src={`data:image/jpeg;base64,${frame}`}
                        alt={`Frame ${index}`}
                        className="rounded-lg border border-slate-700"
                    />
                    )
                )}
                </div>
            </div>
            )}
            
            {!video && (
              <button
                onClick={() => fileInputRef.current?.click()}
                className="w-full py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 shadow-lg hover:shadow-red-500/25 transition-all duration-200"
              >
                Select Video
              </button>
            )}
          </div>

          {/* Footer */}
          <div className="mt-16 text-center text-slate-500 text-sm">
            <p>Powered by Advanced AI & Computer Vision Technology</p>
          </div>
        </div>
      </main>
    </div>
  );
}
