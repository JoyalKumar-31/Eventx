import React, { useState, useRef } from "react";
import { UploadCloud, Image as ImageIcon, X, RefreshCw, AlertCircle, CheckCircle } from "lucide-react";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_SIZE_MB = 10;
const MAX_BYTES = MAX_SIZE_MB * 1024 * 1024;

export const ImageUploadSection = ({
  currentImageUrl = null,
  onImageSelected,
  onImageRemoved,
  uploadStatus = "idle", // 'idle' | 'uploading' | 'uploaded' | 'error'
  errorMessage = null,
}) => {
  const [previewUrl, setPreviewUrl] = useState(currentImageUrl);
  const [dragActive, setDragActive] = useState(false);
  const [validationError, setValidationError] = useState(null);
  const fileInputRef = useRef(null);

  const validateAndSetFile = (file) => {
    setValidationError(null);

    if (!file) return;

    // 1. MIME type validation
    if (!ALLOWED_TYPES.includes(file.type)) {
      setValidationError("Invalid file format. Please upload JPG, PNG, or WEBP.");
      return;
    }

    // 2. File size validation
    if (file.size > MAX_BYTES) {
      setValidationError(`File is too large (${(file.size / (1024 * 1024)).toFixed(1)}MB). Maximum allowed is ${MAX_SIZE_MB}MB.`);
      return;
    }

    // 3. Local object URL preview
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
    if (onImageSelected) {
      onImageSelected(file, objectUrl);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleRemove = () => {
    setPreviewUrl(null);
    setValidationError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    if (onImageRemoved) {
      onImageRemoved();
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-slate-200">
          Event Cover Image <span className="text-indigo-400 font-normal">(16:9 Recommended)</span>
        </label>
        <span className="text-xs text-slate-400">JPG, PNG, WEBP (Max {MAX_SIZE_MB}MB)</span>
      </div>

      {previewUrl ? (
        <div className="relative group overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 aspect-video shadow-md">
          <img
            src={previewUrl}
            alt="Event Cover Preview"
            className="w-full h-full object-cover"
          />

          {/* Overlay Actions on Hover */}
          <div className="absolute inset-0 bg-slate-950/70 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3 backdrop-blur-xs">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Replace Image
            </button>
            <button
              type="button"
              onClick={handleRemove}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-rose-600/80 hover:bg-rose-500 text-white transition-all shadow-md cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
              Remove Image
            </button>
          </div>

          {/* Status Badge */}
          {uploadStatus === "uploading" && (
            <div className="absolute top-3 left-3 px-3 py-1 rounded-lg bg-indigo-950/90 border border-indigo-500/50 text-indigo-300 text-xs flex items-center gap-2 backdrop-blur-md">
              <div className="w-3 h-3 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
              <span>Uploading cover image...</span>
            </div>
          )}

          {uploadStatus === "uploaded" && (
            <div className="absolute top-3 left-3 px-3 py-1 rounded-lg bg-emerald-950/90 border border-emerald-500/50 text-emerald-300 text-xs flex items-center gap-1.5 backdrop-blur-md">
              <CheckCircle className="w-3.5 h-3.5" />
              <span>Image Uploaded</span>
            </div>
          )}
        </div>
      ) : (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center cursor-pointer transition-all aspect-video ${
            dragActive
              ? "border-indigo-500 bg-indigo-500/10"
              : "border-slate-800 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900/60"
          }`}
        >
          <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 mb-3 shadow-sm">
            <UploadCloud className="w-6 h-6 text-indigo-400" />
          </div>

          <p className="text-sm font-medium text-slate-200">
            <span className="text-indigo-400 font-semibold underline underline-offset-2">Click to upload</span> or drag and drop
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Ideal dimensions: 1600 × 900 px (16:9 ratio). High resolution recommended.
          </p>
        </div>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Validation & Server Error Messages */}
      {(validationError || errorMessage) && (
        <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{validationError || errorMessage}</span>
        </div>
      )}
    </div>
  );
};

export default ImageUploadSection;
