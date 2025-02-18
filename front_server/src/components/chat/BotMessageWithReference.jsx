import React from 'react';
import PropTypes from 'prop-types';
import ReactMarkdown from 'react-markdown';
import BotCardContent from './BotCardContent';

export default function BotMessageWithReference({ message, reference }) {
  const formattedContent = `${message}\n\nTo know more:\n[${reference}](${reference})`;

  return (
    <BotCardContent>
      <ReactMarkdown className="prose prose-sm max-w-none">
        {formattedContent}
      </ReactMarkdown>
    </BotCardContent>
  );
}

BotMessageWithReference.propTypes = {
  message: PropTypes.string.isRequired,
  reference: PropTypes.string.isRequired,
};
