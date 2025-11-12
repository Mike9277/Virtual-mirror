import React, { useEffect, useState } from 'react';
import ErrorPage from './ErrorPage.jsx';
import useConfig from './config';

function ApiCheck({ children }) {
  const config = useConfig();
  const [isApiOnline, setIsApiOnline] = useState(null);

  useEffect(() => {
    if (config) {
      fetch(`${config.apiUrl}`)
        .then(response => {
          if (response.ok) {
            setIsApiOnline(true);
          } else {
            setIsApiOnline(false);
          }
        })
        .catch(() => setIsApiOnline(false));
    }
  }, [config]);

  if (!config) {
    return <div className='error'>Loading configuration...</div>;
  }

  if (isApiOnline === null) {
    return <div className='error'>Checking API status...</div>;
  }

  if (!isApiOnline) {
    return <ErrorPage />;
  }

  return children;
}

export default ApiCheck;

