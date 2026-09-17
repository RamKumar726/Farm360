import { useState, useRef } from "react";
import { Upload, X, Image, Video, Check } from "lucide-react";

export default function ProofUploader({ onUpload, farmId, accept = "image/*,video/*" }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState([]);
  const fileRef = useRef();

  const handleFiles = (e) => {
    const selected = Array.from(e.target.files);
    setFiles((prev) => [...prev, ...selected]);
  };

  const removeFile = (idx) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  const uploadToCloudinary = async () => {
    const cloudName = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME;
    const uploadPreset = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET;
    if (!cloudName || !uploadPreset) {
      alert("Cloudinary not configured. Set VITE_CLOUDINARY_CLOUD_NAME and VITE_CLOUDINARY_UPLOAD_PRESET in .env");
      return;
    }
    setUploading(true);
    const urls = [];
    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("upload_preset", uploadPreset);
        formData.append("folder", `farm360/proof/${farmId || "general"}`);
        const res = await fetch(`https://api.cloudinary.com/v1_1/${cloudName}/upload`, {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        urls.push(data.secure_url);
      }
      setUploaded(urls);
      onUpload?.(urls);
      setFiles([]);
    } catch (e) {
      console.error("Upload failed:", e);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        className="border-2 border-dashed border-white/20 rounded-2xl p-8 text-center cursor-pointer
                   hover:border-accent/40 hover:bg-accent/5 transition-all duration-300"
        onClick={() => fileRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          setFiles((prev) => [...prev, ...Array.from(e.dataTransfer.files)]);
        }}
      >
        <Upload className="mx-auto text-[#8fac9a] mb-3" size={36} />
        <p className="text-[#8fac9a]">Drag & drop photos/videos or <span className="text-accent underline">browse</span></p>
        <p className="text-xs text-[#8fac9a]/60 mt-1">GPS metadata will be captured automatically</p>
        <input ref={fileRef} type="file" accept={accept} multiple onChange={handleFiles} className="hidden" />
      </div>

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((f, i) => (
            <div key={i} className="flex items-center gap-3 bg-white/5 rounded-xl px-4 py-2">
              {f.type.startsWith("video") ? <Video size={16} className="text-blue-400" /> : <Image size={16} className="text-green-400" />}
              <span className="text-sm flex-1 truncate">{f.name}</span>
              <span className="text-xs text-[#8fac9a]">{(f.size / 1024).toFixed(0)} KB</span>
              <button onClick={() => removeFile(i)} className="text-red-400 hover:text-red-300">
                <X size={14} />
              </button>
            </div>
          ))}
          <button
            onClick={uploadToCloudinary}
            disabled={uploading}
            className="btn-primary w-full mt-2"
          >
            {uploading ? "Uploading..." : `Upload ${files.length} file${files.length > 1 ? "s" : ""}`}
          </button>
        </div>
      )}

      {/* Uploaded URLs */}
      {uploaded.length > 0 && (
        <div className="space-y-1">
          {uploaded.map((url, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-green-400">
              <Check size={14} /> <a href={url} target="_blank" rel="noreferrer" className="underline truncate">{url.slice(0, 60)}...</a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
