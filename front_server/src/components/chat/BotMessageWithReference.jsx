import React, { useState } from 'react';
import PropTypes from 'prop-types';
import ReactMarkdown from 'react-markdown';
import BotCardContent from './BotCardContent';
import { Button } from '@components/ui/button';

export default function BotMessageWithReference({ message, reference }) {
  const [showAll, setShowAll] = useState(false);
  const initialDisplayCount = 3;
  
  const displayedReferences = showAll ? reference : reference?.slice(0, initialDisplayCount);
  const hasMore = reference?.length > initialDisplayCount;

  return (
    <BotCardContent>
      <div className="flex flex-col gap-2">
        <div className="prose prose-sm max-w-none prose-p:my-1 prose-headings:my-2">
          <ReactMarkdown>{message}</ReactMarkdown>
        </div>
        {reference && reference.length > 0 && (
          <div className="text-xs text-gray-500 mt-2 border-t pt-2">
            <span className="font-medium">참고 자료:</span>
            <ul className="list-none mt-1 space-y-1">
              {displayedReferences.map((ref, index) => (
                <li key={index}>
                  <a 
                    href={ref.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:text-blue-700 underline"
                  >
                    {ref.title}
                  </a>
                </li>
              ))}
            </ul>
            {hasMore && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAll(!showAll)}
                className="mt-2 text-xs text-gray-500 hover:text-gray-700"
              >
                {showAll ? '접기' : `더보기 (${reference.length - initialDisplayCount})`}
              </Button>
            )}
          </div>
        )}
      </div>
    </BotCardContent>
  );
}

BotMessageWithReference.propTypes = {
  message: PropTypes.string.isRequired,
  reference: PropTypes.arrayOf(PropTypes.shape({
    title: PropTypes.string.isRequired,
    url: PropTypes.string.isRequired,
  })),
};
