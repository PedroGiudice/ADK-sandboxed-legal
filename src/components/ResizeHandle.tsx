import React, { useCallback, useEffect, useState } from 'react';

interface ResizeHandleProps {
  direction: 'horizontal' | 'vertical';
  onResize: (delta: number) => void;
  className?: string;
}

/**
 * Draggable resize handle component
 * - horizontal: resizes left/right (for sidebar)
 * - vertical: resizes up/down (for input area)
 */
const ResizeHandle: React.FC<ResizeHandleProps> = ({ direction, onResize, className = '' }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [startPos, setStartPos] = useState(0);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    setStartPos(direction === 'horizontal' ? e.clientX : e.clientY);
  }, [direction]);

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      const currentPos = direction === 'horizontal' ? e.clientX : e.clientY;
      const delta = currentPos - startPos;
      setStartPos(currentPos);
      onResize(delta);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, startPos, direction, onResize]);

  const baseClasses = direction === 'horizontal'
    ? 'w-2 cursor-col-resize hover:bg-accent/30 active:bg-accent/50'
    : 'h-2 cursor-row-resize hover:bg-accent/30 active:bg-accent/50';

  return (
    <div
      onMouseDown={handleMouseDown}
      className={`
        ${baseClasses}
        bg-transparent transition-colors duration-150 flex-shrink-0
        ${isDragging ? 'bg-accent/50' : ''}
        ${className}
      `}
    >
      {/* Visual indicator */}
      <div className={`
        ${direction === 'horizontal' ? 'w-0.5 h-8 mx-auto my-auto' : 'h-0.5 w-8 mx-auto my-auto'}
        bg-border-subtle rounded-full opacity-0 hover:opacity-100 transition-opacity
        ${isDragging ? 'opacity-100 bg-accent' : ''}
      `} />
    </div>
  );
};

export default ResizeHandle;

/**
 * Custom hook for managing resizable panel dimensions
 */
export const useResizable = (
  initialSize: number,
  minSize: number,
  maxSize: number,
  storageKey?: string
) => {
  const [size, setSize] = useState(() => {
    if (storageKey) {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = parseInt(saved, 10);
        if (!isNaN(parsed) && parsed >= minSize && parsed <= maxSize) {
          return parsed;
        }
      }
    }
    return initialSize;
  });

  const handleResize = useCallback((delta: number) => {
    setSize(prev => {
      const newSize = Math.max(minSize, Math.min(maxSize, prev + delta));
      if (storageKey) {
        localStorage.setItem(storageKey, String(newSize));
      }
      return newSize;
    });
  }, [minSize, maxSize, storageKey]);

  return { size, handleResize, setSize };
};
