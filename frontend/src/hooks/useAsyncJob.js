import { useState, useRef, useEffect, useCallback } from 'react';

/**
 * Hook implementing the Section 2.1 Pattern B async job execution contract:
 * - Executes the async task with AbortController cancellation
 * - Manages honest step progression and elapsed time
 * - Protects against unmount leaks
 */
export function useAsyncJob() {
  const [isRunning, setIsRunning] = useState(false);
  const [step, setStep] = useState('');
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState(null);

  const abortControllerRef = useRef(null);
  const timerRef = useRef(null);

  const cleanup = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsRunning(false);
    setElapsed(0);
  }, []);

  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  /**
   * Run an async operation with simulated honest progress steps
   * @param {Array<{ message: string, delayMs: number }>} steps
   * @param {Function} asyncFn - Receives { signal }
   * @returns {Promise<any>}
   */
  const runJob = useCallback(
    async (steps = [], asyncFn) => {
      cleanup();

      const controller = new AbortController();
      abortControllerRef.current = controller;

      setIsRunning(true);
      setError(null);
      setElapsed(0);

      // Start elapsed timer
      const startTime = Date.now();
      timerRef.current = setInterval(() => {
        setElapsed(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);

      // Sequence initial step
      if (steps.length > 0) {
        setStep(steps[0].message);
      }

      // Step progression tracker
      let stepIndex = 0;
      const stepTimer = setInterval(() => {
        stepIndex += 1;
        if (stepIndex < steps.length) {
          setStep(steps[stepIndex].message);
        } else {
          clearInterval(stepTimer);
        }
      }, steps[0]?.delayMs || 1500);

      try {
        const result = await asyncFn({ signal: controller.signal });
        clearInterval(stepTimer);
        cleanup();
        return result;
      } catch (err) {
        clearInterval(stepTimer);
        cleanup();
        if (controller.signal.aborted) {
          return null;
        }
        const message =
          err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          'Operation failed. Please check your connection and try again.';
        setError(message);
        throw err;
      }
    },
    [cleanup]
  );

  const cancelJob = useCallback(() => {
    cleanup();
  }, [cleanup]);

  return {
    isRunning,
    step,
    elapsed,
    error,
    runJob,
    cancelJob,
  };
}

export default useAsyncJob;
