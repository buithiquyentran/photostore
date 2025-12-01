import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface ProgressBarProps {
  isLoading: boolean;
  progress?: number; // 0-100, optional for indeterminate mode
}

/**
 * Modern top progress bar for API calls
 * Features:
 * - Smooth animations with Framer Motion
 * - Auto-progress simulation when progress not provided
 * - Sticks to top of viewport
 * - Gradient effect
 */
export const ProgressBar: React.FC<ProgressBarProps> = ({
  isLoading,
  progress,
}) => {
  const [currentProgress, setCurrentProgress] = useState(0);

  useEffect(() => {
    if (!isLoading) {
      // Complete animation when done
      setCurrentProgress(100);
      const timer = setTimeout(() => setCurrentProgress(0), 500);
      return () => clearTimeout(timer);
    }

    if (progress !== undefined) {
      // Use provided progress
      setCurrentProgress(progress);
    } else {
      // Auto-simulate progress (asymptotic approach to 90%)
      setCurrentProgress(0);
      const interval = setInterval(() => {
        setCurrentProgress((prev) => {
          if (prev >= 90) return prev;
          // Slower as it approaches 90%
          const increment = (90 - prev) * 0.1;
          return Math.min(prev + increment, 90);
        });
      }, 300);

      return () => clearInterval(interval);
    }
  }, [isLoading, progress]);

  return (
    <AnimatePresence>
      {isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed top-0 left-0 right-0 z-[9999] h-1 bg-transparent"
        >
          <motion.div
            className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 shadow-lg"
            initial={{ width: "0%" }}
            animate={{
              width: `${currentProgress}%`,
              transition: {
                duration: 0.3,
                ease: "easeOut",
              },
            }}
          >
            {/* Glowing effect */}
            <div className="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-white/50 to-transparent" />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ProgressBar;
