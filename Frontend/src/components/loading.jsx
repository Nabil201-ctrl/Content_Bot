import React from 'react';
import Dither from './Dither';
import { BlinkBlur } from 'react-loading-indicators';

function Loading() {
  return (
    <>
      <div style={{ width: '100%', height: '600px', position: 'relative' }}>
        <Dither
          waveColor={[0.5, 0.5, 0.5]}
          disableAnimation={false}
          enableMouseInteraction={true}
          mouseRadius={0.3}
          colorNum={4}
          waveAmplitude={0.3}
          waveFrequency={3}
          waveSpeed={0.05}
        />
      </div>

      <div className="flex flex-col justify-center items-center h-screen w-full bg-gray-200">
        {/* Use BlinkBlur from react-loading-indicators (falls back to CSS spinner if not available) */}
        {typeof BlinkBlur === 'function' ? (
          <BlinkBlur color="#040404" size="large" text="Loading" textColor="#121111" />
        ) : (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900 mb-4" />
            <div className="text-gray-900 font-medium">Loading...</div>
          </>
        )}
      </div>
    </>
  );
}

export default Loading;