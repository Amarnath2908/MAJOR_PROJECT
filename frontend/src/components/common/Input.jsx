import React, { forwardRef } from 'react';

export const Input = forwardRef(function Input(
  {
    label,
    error,
    helperText,
    leftIcon,
    rightIcon,
    className = '',
    containerClassName = '',
    id,
    ...props
  },
  ref
) {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

  return (
    <div className={`flex flex-col gap-1.5 ${containerClassName}`}>
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-slate-300">
          {label}
        </label>
      )}

      <div className="relative flex items-center">
        {leftIcon && (
          <span className="absolute left-3.5 text-slate-400 pointer-events-none flex items-center">
            {leftIcon}
          </span>
        )}

        <input
          ref={ref}
          id={inputId}
          className={`w-full bg-slate-900/90 text-slate-100 border rounded-xl py-2.5 px-3.5 text-sm transition-all duration-200 placeholder:text-slate-500 focus:outline-none focus:ring-2 ${
            error
              ? 'border-red-500/80 focus:ring-red-500/50 focus:border-red-500'
              : 'border-slate-700/80 hover:border-slate-600 focus:ring-brand-500/50 focus:border-brand-500'
          } ${leftIcon ? 'pl-10' : ''} ${rightIcon ? 'pr-10' : ''} ${className}`}
          {...props}
        />

        {rightIcon && (
          <span className="absolute right-3.5 text-slate-400 flex items-center">
            {rightIcon}
          </span>
        )}
      </div>

      {error ? (
        <p className="text-xs text-red-400 mt-0.5">{error}</p>
      ) : helperText ? (
        <p className="text-xs text-slate-400 mt-0.5">{helperText}</p>
      ) : null}
    </div>
  );
});

export default Input;
