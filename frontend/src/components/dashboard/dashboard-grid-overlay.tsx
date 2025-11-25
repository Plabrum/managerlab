'use client';

/**
 * Grid overlay showing dashed lines for the 6-column layout
 * Only visible in edit mode
 */
export function DashboardGridOverlay() {
  return (
    <div className="pointer-events-none absolute inset-0 z-0">
      {/* Vertical lines - 6 columns */}
      <div className="absolute inset-y-0 left-6 right-6 flex justify-between border border-blue-500">
        {Array.from({ length: 7 }).map((_, i) => (
          <div
            key={`v-${i}`}
            className="border-border/60 h-full w-px border-l-2 border-dashed"
          />
        ))}
      </div>
      {/* Horizontal lines - rows of 100px + 24px gap */}
      <div className="absolute inset-x-0 left-6 right-6  border border-red-500">
        {Array.from({ length: 20 }).map((_, i) => (
          <div
            key={`h-${i}`}
            className="border-border/60 w-full border-t-2 border-dashed"
            style={{ marginTop: i === 0 ? 0 : '110px' }}
          />
        ))}
      </div>
    </div>
  );
}
