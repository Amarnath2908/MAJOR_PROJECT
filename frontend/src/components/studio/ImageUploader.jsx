import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, X, AlertCircle } from 'lucide-react';
import Button from '../common/Button';
import { validateImageFile, formatBytes, MAX_FILE_SIZE_MB } from '../../utils/fileValidation';

export function ImageUploader({ onImageSelected, isUploading, uploadProgress }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [validationError, setValidationError] = useState(null);
  const inputRef = useRef(null);

  const handleFile = (file) => {
    setValidationError(null);
    if (!file) return;

    const validation = validateImageFile(file);
    if (!validation.valid) {
      setValidationError(validation.error);
      return;
    }

    setSelectedFile(file);
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const clearSelection = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setValidationError(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const handleSubmit = () => {
    if (selectedFile && onImageSelected) {
      onImageSelected(selectedFile, previewUrl);
    }
  };

  return (
    <div className="w-full flex flex-col items-center justify-center">
      {!previewUrl ? (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`w-full max-w-xl h-80 border-2 border-dashed rounded-3xl flex flex-col items-center justify-center p-8 text-center cursor-pointer transition-all duration-200 ${
            dragActive
              ? 'border-brand-400 bg-brand-500/10 scale-[1.01]'
              : 'border-slate-700/80 bg-slate-900/50 hover:border-slate-600 hover:bg-slate-900/80'
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp,image/bmp,image/tiff"
            onChange={handleChange}
            className="hidden"
          />

          <div className="w-16 h-16 rounded-2xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-400 mb-4 shadow-glow/30">
            <UploadCloud className="w-8 h-8 animate-bounce-slow" />
          </div>

          <h3 className="text-base font-semibold text-white">
            Drag & drop your room or space image
          </h3>
          <p className="text-xs text-slate-400 mt-1 mb-4">
            Supports JPG, PNG, WEBP up to {MAX_FILE_SIZE_MB} MB
          </p>

          <Button size="sm" variant="secondary" onClick={(e) => { e.stopPropagation(); inputRef.current?.click(); }}>
            Browse Files
          </Button>

          {validationError && (
            <div className="mt-4 p-2.5 bg-red-950/60 border border-red-800/80 rounded-xl flex items-center gap-2 text-xs text-red-300">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{validationError}</span>
            </div>
          )}
        </div>
      ) : (
        <div className="w-full max-w-xl flex flex-col items-center gap-4">
          <div className="relative w-full aspect-video rounded-2xl overflow-hidden border border-slate-700/80 bg-slate-950 shadow-2xl group">
            <img
              src={previewUrl}
              alt="Selected preview"
              className="w-full h-full object-cover"
            />

            {!isUploading && (
              <button
                onClick={clearSelection}
                className="absolute top-3 right-3 p-1.5 rounded-xl bg-dark-900/80 hover:bg-red-600 text-slate-300 hover:text-white backdrop-blur-md transition-all shadow-lg cursor-pointer"
                title="Remove image"
              >
                <X className="w-4 h-4" />
              </button>
            )}

            <div className="absolute bottom-0 inset-x-0 p-3 bg-gradient-to-t from-dark-900/90 via-dark-900/60 to-transparent flex items-center justify-between text-xs text-slate-300">
              <div className="flex items-center gap-2 truncate">
                <ImageIcon className="w-4 h-4 text-brand-400" />
                <span className="truncate font-medium">{selectedFile.name}</span>
              </div>
              <span className="text-slate-400 ml-2">{formatBytes(selectedFile.size)}</span>
            </div>
          </div>

          {validationError && (
            <div className="w-full p-2.5 bg-red-950/60 border border-red-800/80 rounded-xl flex items-center gap-2 text-xs text-red-300">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{validationError}</span>
            </div>
          )}

          <div className="flex items-center gap-3 w-full justify-end">
            <Button variant="ghost" size="sm" onClick={clearSelection} disabled={isUploading}>
              Change Image
            </Button>
            <Button
              size="md"
              onClick={handleSubmit}
              isLoading={isUploading}
              leftIcon={<UploadCloud className="w-4 h-4" />}
            >
              {isUploading ? `Uploading (${uploadProgress || 0}%)...` : 'Upload & Analyze Space'}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default ImageUploader;
