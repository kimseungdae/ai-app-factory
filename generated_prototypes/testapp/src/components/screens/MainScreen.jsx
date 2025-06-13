import React from 'react';
import Button from '../common/Button';

const MainScreen = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Welcome to TestApp
          </h1>
          <p className="text-gray-600 mb-6">
            This is your new React application built with Tailwind CSS.
          </p>
          <Button variant="primary" size="lg">
            Get Started
          </Button>
        </div>
      </div>
    </div>
  );
};

export default MainScreen;