import React from 'react';
import Button from './Button';

export function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  className = '',
}) {
  return (
    <div
      className={`flex flex-col items-center justify-center text-center p-8 border border-dashed border-slate-800 rounded-2xl bg-dark-850/50 ${className}`}
    >
      {icon && <div className="p-3 bg-slate-800/80 rounded-2xl text-brand-400 mb-4">{icon}</div>}
      <h3 className="text-base font-semibold text-slate-200">{title}</h3>
      {description && <p className="text-sm text-slate-400 max-w-sm mt-1.5 mb-5">{description}</p>}
      {actionLabel && onAction && (
        <Button onClick={onAction} size="sm">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

export default EmptyState;
