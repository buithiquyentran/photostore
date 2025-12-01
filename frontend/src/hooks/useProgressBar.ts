import { useState, useEffect } from "react";

interface ProgressBarState {
  isLoading: boolean;
  progress?: number;
}

let globalSetLoading: ((state: ProgressBarState) => void) | null = null;

/**
 * Hook to manage global progress bar state
 * Usage:
 *   const { startLoading, stopLoading, setProgress } = useProgressBar();
 */
export const useProgressBar = () => {
  const [state, setState] = useState<ProgressBarState>({
    isLoading: false,
    progress: undefined,
  });

  useEffect(() => {
    globalSetLoading = setState;
    return () => {
      globalSetLoading = null;
    };
  }, []);

  const startLoading = (progress?: number) => {
    setState({ isLoading: true, progress });
  };

  const stopLoading = () => {
    setState({ isLoading: false, progress: undefined });
  };

  const setProgress = (progress: number) => {
    setState((prev) => ({ ...prev, progress }));
  };

  return {
    ...state,
    startLoading,
    stopLoading,
    setProgress,
  };
};

/**
 * Global functions to control progress bar from anywhere
 * (e.g., axios interceptors)
 */
export const showProgressBar = (progress?: number) => {
  if (globalSetLoading) {
    globalSetLoading({ isLoading: true, progress });
  }
};

export const hideProgressBar = () => {
  if (globalSetLoading) {
    globalSetLoading({ isLoading: false, progress: undefined });
  }
};

export const updateProgress = (progress: number) => {
  if (globalSetLoading) {
    globalSetLoading((prev) => ({ ...prev, progress }));
  }
};
