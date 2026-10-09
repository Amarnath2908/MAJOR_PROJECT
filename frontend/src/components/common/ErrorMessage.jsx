import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';
import Button from './Button';

export function ErrorMessage({
  title = 'Something went wrong',
  message,
  onRetry,
  className = '',
}) {
  return (
    <div
      className={`p-4 bg-red-950/40 border border-red-800/60 rounded-xl flex items-start gap-3.5 ${className}`}
      role="alert"
    >
      <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-semibold text-red-200">{title}</h4>
        {message && <p className="text-xs text-red-300/90 mt-1 leading-relaxed">{message}</p>}
        {onRetry && (
          <div className="mt-3">
            <Button
              size="sm"
              variant="outline"
              onClick={onRetry}
              leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
              className="border-red-600/50 text-red-200 hover:bg-red-900/30"
            >
              Try Again
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

export default ErrorMessage;
