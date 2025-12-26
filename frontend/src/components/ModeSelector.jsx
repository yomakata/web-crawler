import { useState } from 'react';
import { FiCheckCircle, FiCircle } from 'react-icons/fi';

const ModeSelector = ({ mode, onChange }) => {
  const modes = [
    {
      id: 'content',
      title: 'Content Mode',
      description: 'Extract and save webpage content in multiple formats (txt, md, html)',
      features: ['Text extraction', 'Markdown conversion', 'HTML formatting', 'Image downloading', 'Content scoping']
    },
    {
      id: 'link',
      title: 'Link Mode',
      description: 'Extract only hyperlinks from the webpage',
      features: ['Internal links', 'External links', 'Link filtering', 'JSON metadata', 'Link statistics']
    }
  ];

  return (
    <div className="mb-6">
      <label className="block text-sm font-semibold text-gray-700 mb-3">
        Select Crawling Mode
      </label>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {modes.map((m) => (
          <button
            key={m.id}
            type="button"
            onClick={() => onChange(m.id)}
            className={`relative p-5 rounded-lg border-2 transition-all text-left ${
              mode === m.id
                ? 'border-primary-500 bg-primary-50 shadow-md'
                : 'border-gray-200 bg-white hover:border-primary-300 hover:shadow-sm'
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <h3 className="text-lg font-bold text-gray-900">{m.title}</h3>
              <div className={`text-2xl ${mode === m.id ? 'text-primary-500' : 'text-gray-300'}`}>
                {mode === m.id ? <FiCheckCircle /> : <FiCircle />}
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-3">{m.description}</p>
            <ul className="space-y-1">
              {m.features.map((feature, idx) => (
                <li key={idx} className="text-xs text-gray-500 flex items-center">
                  <span className="w-1 h-1 bg-primary-400 rounded-full mr-2"></span>
                  {feature}
                </li>
              ))}
            </ul>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ModeSelector;
